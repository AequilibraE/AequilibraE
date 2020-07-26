import math
import os
from warnings import warn
from sqlite3 import Connection as sqlc
from typing import List, Dict
import numpy as np
from aequilibrae.project.network import OSMDownloader
from aequilibrae.project.network.osm_builder import OSMBuilder
from aequilibrae.project.network.osm_utils.place_getter import placegetter
from aequilibrae.project.network.osm_utils.osm_params import max_query_area_size
from aequilibrae.project.network.haversine import haversine
from aequilibrae.project.network.modes import Modes
from aequilibrae.project.network.link_types import LinkTypes
from aequilibrae.paths import Graph
from aequilibrae.parameters import Parameters
from aequilibrae import logger
from aequilibrae.project.project_creation import req_link_flds, req_node_flds, protected_fields


class Network():
    """
    Network class. Member of an AequilibraE Project
    """
    req_link_flds = req_link_flds
    req_node_flds = req_node_flds
    protected_fields = protected_fields
    link_types: LinkTypes = None

    def __init__(self, project) -> None:
        self.conn = project.conn  # type: sqlc
        self.source = project.source  # type: sqlc
        self.graphs = {}  # type: Dict[Graph]
        self.modes = Modes(self)
        self.link_types = LinkTypes(self)

    # TODO: DOCUMENT THESE FUNCTIONS
    def skimmable_fields(self):
        """
        Returns a list of all fields that can be skimmed

        Returns:
            :obj:`list`: List of all fields that can be skimmed
        """
        curr = self.conn.cursor()
        curr.execute('PRAGMA table_info(links);')
        field_names = curr.fetchall()
        ignore_fields = ['ogc_fid', 'geometry'] + self.req_link_flds

        skimmable = ['INT', 'INTEGER', 'TINYINT', 'SMALLINT', 'MEDIUMINT', 'BIGINT', 'UNSIGNED BIG INT',
                     'INT2', 'INT8', 'REAL', 'DOUBLE', 'DOUBLE PRECISION', 'FLOAT', 'DECIMAL', 'NUMERIC']
        all_fields = []

        for f in field_names:
            if f[1] in ignore_fields:
                continue
            for i in skimmable:
                if i in f[2].upper():
                    all_fields.append(f[1])
                    break

        all_fields.append('distance')
        real_fields = []
        for f in all_fields:
            if f[-2:] == "ab":
                if f[:-2] + 'ba' in all_fields:
                    real_fields.append(f[:-3])
            elif f[-3:] == "_ba":
                pass
            else:
                real_fields.append(f)

        return real_fields

    def modes(self):
        """
        Returns a list of all the modes in this model

        Returns:
            :obj:`list`: List of all modes
        """
        curr = self.conn.cursor()
        curr.execute("""select mode_id from modes""")
        return [x[0] for x in curr.fetchall()]

    def create_from_osm(
            self,
            west: float = None,
            south: float = None,
            east: float = None,
            north: float = None,
            place_name: str = None,
            modes=["car", "transit", "bicycle", "walk"],
            spatial_index=False,
    ) -> None:
        """
        Downloads the network from Open-Street Maps

        Args:
            *west* (:obj:`float`, Optional): West most coordinate of the download bounding box

            *south* (:obj:`float`, Optional): South most coordinate of the download bounding box

            *east* (:obj:`float`, Optional): East most coordinate of the download bounding box

            *place_name* (:obj:`str`, Optional): If not downloading with East-West-North-South boundingbox, this is
            required

            *modes* (:obj:`list`, Optional): List of all modes to be downloaded. Defaults to the modes in the parameter
            file

            *spatial_index* (:obj:`bool`, Optional): Creates spatial index. Defaults to zero. REQUIRES SQLITE WITH RTREE
        """

        if self.count_links() > 0:
            raise FileExistsError("You can only import an OSM network into a brand new model file")

        curr = self.conn.cursor()
        curr.execute("""ALTER TABLE links ADD COLUMN osm_id integer""")
        curr.execute("""ALTER TABLE nodes ADD COLUMN osm_id integer""")
        self.conn.commit()

        if isinstance(modes, (tuple, list)):
            modes = list(modes)
        elif isinstance(modes, str):
            modes = [modes]
        else:
            raise ValueError("'modes' needs to be string or list/tuple of string")

        if place_name is None:
            if min(east, west) < -180 or max(east, west) > 180 or min(north, south) < -90 or max(north, south) > 90:
                raise ValueError("Coordinates out of bounds")
            bbox = [west, south, east, north]
        else:
            bbox, report = placegetter(place_name)
            west, south, east, north = bbox
            if bbox is None:
                msg = f'We could not find a reference for place name "{place_name}"'
                warn(msg)
                logger.warning(msg)
                return
            for i in report:
                if "PLACE FOUND" in i:
                    logger.info(i)

        # Need to compute the size of the bounding box to not exceed it too much
        height = haversine((east + west) / 2, south, (east + west) / 2, north)
        width = haversine(east, (north + south) / 2, west, (north + south) / 2)
        area = height * width

        if area < max_query_area_size:
            polygons = [bbox]
        else:
            polygons = []
            parts = math.ceil(area / max_query_area_size)
            horizontal = math.ceil(math.sqrt(parts))
            vertical = math.ceil(parts / horizontal)
            dx = east - west
            dy = north - south
            for i in range(horizontal):
                xmin = max(-180, west + i * dx)
                xmax = min(180, west + (i + 1) * dx)
                for j in range(vertical):
                    ymin = max(-90, south + j * dy)
                    ymax = min(90, south + (j + 1) * dy)
                    box = [xmin, ymin, xmax, ymax]
                    polygons.append(box)

        logger.info("Downloading data")
        self.downloader = OSMDownloader(polygons, modes)
        self.downloader.doWork()

        logger.info("Building Network")
        self.builder = OSMBuilder(self.downloader.json, self.source)
        self.builder.doWork()

        if spatial_index:
            logger.info("Adding spatial indices")
            self.add_spatial_index()

        logger.info("Network built successfully")

    def build_graphs(self) -> None:
        """Builds graphs for all modes currently available in the model

        When called, it overwrites all graphs previously created and stored in the networks'
        dictionary of graphs
        """
        curr = self.conn.cursor()
        curr.execute('PRAGMA table_info(links);')
        field_names = curr.fetchall()

        ignore_fields = ['ogc_fid', 'geometry']
        all_fields = [f[1] for f in field_names if f[1] not in ignore_fields]

        raw_links = curr.execute(f"select {','.join(all_fields)} from links").fetchall()
        links = []
        for lnk in raw_links:
            lk = list(map(lambda x: np.nan if x is None else x, lnk))
            links.append(lk)

        data = np.core.records.fromrecords(links, names=all_fields)

        valid_fields = []
        removed_fields = []
        for f in all_fields:
            if np.issubdtype(data[f].dtype, np.floating) or np.issubdtype(data[f].dtype, np.integer):
                valid_fields.append(f)
            else:
                removed_fields.append(f)
        if len(removed_fields) > 1:
            warn(f'Fields were removed form Graph for being non-numeric: {",".join(removed_fields)}')

        curr.execute('select node_id from nodes where is_centroid=1;')
        centroids = np.array([i[0] for i in curr.fetchall()], np.uint32)

        modes = curr.execute('select mode_id from modes;').fetchall()
        modes = [m[0] for m in modes]

        for m in modes:
            w = np.core.defchararray.find(data['modes'], m)
            net = np.array(data[valid_fields], copy=True)
            net['b_node'][w < 0] = net['a_node'][w < 0]

            g = Graph()
            g.mode = m
            g.network = net
            g.network_ok = True
            g.status = 'OK'
            g.prepare_graph(centroids)
            g.set_blocked_centroid_flows(True)
            self.graphs[m] = g

    def set_time_field(self, time_field: str) -> None:
        """
        Set the time field for all graphs built in the model

        Args:
            *time_field* (:obj:`str`): Network field with travel time information
        """
        for m, g in self.graphs.items():  # type: str, Graph
            if time_field not in list(g.graph.dtype.names):
                raise ValueError(f"{time_field} not available. Check if you have NULL values in the database")
            g.free_flow_time = time_field
            g.set_graph(time_field)
            self.graphs[m] = g

    def count_links(self) -> int:
        """
        Returns the number of links in the model

        Returns:
            :obj:`int`: Number of links
        """
        return self.__count_items('link_id', 'links', 'link_id>=0')

    def count_centroids(self) -> int:
        """
        Returns the number of centroids in the model

        Returns:
            :obj:`int`: Number of centroids
        """
        return self.__count_items('node_id', 'nodes', 'is_centroid=1')

    def count_nodes(self) -> int:
        """
        Returns the number of nodes in the model

        Returns:
            :obj:`int`: Number of nodes
        """
        return self.__count_items('node_id', 'nodes', 'node_id>=0')

    def add_centroid(self, node_id: int, coords: List[float], modes: str) -> None:
        """
               Adds a centroid and centroid connectors for the desired modes to the network file

               Args:
                   *node_id* (:obj:`int`): ID for the centroid to be included in the network

                   *coords* (:obj:`List`): XY Coordinates for centroid -> [LONGITUDE, LATITUDE]

                   *modes* (:obj:`str`): Modes for which centroids connectors should be added
               """
        pass

    def add_spatial_index(self) -> None:
        """Adds spatial indices to links and nodes table

        Requires an Sqlite3 distribution with RTree (not the Python standard).
        Use with caution"""
        curr = self.conn.cursor()
        curr.execute("""SELECT CreateSpatialIndex( 'links' , 'geometry' );""")
        curr.execute("""SELECT CreateSpatialIndex( 'nodes' , 'geometry' );""")
        self.conn.commit()

    def __count_items(self, field: str, table: str, condition: str) -> int:
        c = self.conn.cursor()
        c.execute(f"""select count({field}) from {table} where {condition};""")
        return c.fetchone()[0]

    def __del__(self):
        for obj in [self.link_types, self.modes]:
            del obj

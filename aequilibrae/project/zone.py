import string
from .network.safe_class import SafeClass
from aequilibrae.project.database_connection import database_connection


class Zone(SafeClass):
    """Single zone object that can be queried and manipulated in memory"""
    def __init__(self, dataset: dict, zoning):
        super().__init__(dataset)
        self.__zoning = zoning
        self.__new = dataset['geometry'] is None

    def delete(self):
        """Removes the zone from the database"""
        conn = database_connection()
        curr = conn.cursor()
        curr.execute(f'DELETE FROM zones where zone_id="{self.zone_id}"')
        conn.commit()
        self.__zoning._remove_zone(self.zone_id)
        del self

    def save(self):
        """Saves/Updates the zone data to the database"""

        if self.zone_id != self.__original__['zone_id']:
            raise ValueError('One cannot change the zone_id')

        conn = database_connection()
        curr = conn.cursor()

        curr.execute(f'select count(*) from zones where zone_id="{self.zone_id}"')
        if curr.fetchone()[0] == 0:
            data = [self.zone_id, self.geometry.wkb]
            curr.execute('Insert into zones (zone_id, geometry) values(?, ST_Multi(GeomFromWKB(?, 4326)))', data)

        for key, value in self.__dict__.items():
            if key != 'zone_id' and key in self.__original__:
                v_old = self.__original__.get(key, None)
                if value != v_old and value is not None:
                    self.__original__[key] = value
                    if key == 'geometry':
                        sql = "update 'zones' set geometry=ST_Multi(GeomFromWKB(?, 4326)) where zone_id=?"
                        curr.execute(sql, [value.wkb, self.zone_id])
                    else:
                        curr.execute(f"update 'zones' set '{key}'=? where zone_id=?", [value, self.zone_id])
        conn.commit()
        conn.close()

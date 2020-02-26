Use examples
============
This page is still under development, so most of the headers are just place-holders for the actual examples

.. note::
   The examples provided here are not meant as a through description of
   AequilibraE's capabilities. For that, please look into the API documentation
   or email aequilibrae@googlegroups.com

.. _example_logging:

Logging
-------
AequilibraE uses Python's standard logging library to a file called
*aequilibrae.log*, but the output folder for this logging can be changed to a
custom system folder by altering the parameter **system --> logging_directory** on
the parameters file.

As an example, one could do programatically change the output folder to
*'D:/myProject/logs'* by doing the following:

::

  from aequilibrae import Parameters

  fldr = 'D:/myProject/logs'

  p = Parameters()
  p.parameters['system']['logging_directory'] =  fldr
  p.writeback()

The other useful resource, especially during model debugging it to also show
all log messages directly on the screen. Doing that requires a little knowledge
of the Python Logging library, but it is just as easy:

::

  from aequilibrae import logger
  import logging

  stdout_handler = logging.StreamHandler(sys.stdout)
  logger.addHandler(stdout_handler)

.. _example_usage_parameters:

Parameters module
-----------------
Several examples on how to manipulate the parameters within AequilibraE have
been shown in other parts of this tutorial.

However, in case you ever have trouble with parameter changes you have made,
you can always revert them to their default values. But remember, **ALL**
**CHANGES WILL BE LOST**.

::

  from aequilibrae import Parameters

  fldr = 'D:/myProject/logs'

  p = Parameters()
  p.reset_default()


.. _example_usage_matrix:

Matrix module
-------------

* **AequilibraEMatrix**
* **AequilibraEData**


.. _example_usage_project:

Project module
--------------

Let's suppose one wants to create project files for a list of 5 cities around
the world with their complete networks downloaded from
`Open Street Maps <http://www.openstreetmap.org>`_ and place them on a local
folder for analysis at a later time.


::

  from aequilibrae.project import Project

  cities = ["Darwin, Australia",
            "Karlsruhe, Germany",
            "London, UK",
            "Paris, France",
            "Auckland, New Zealand"]

  for city in cities:
      print(city)
      pth = f'd:/net_tests/{city}.sqlite'

      p = Project(pth, True)
      p.network.create_from_osm(place_name=city)
      p.conn.close()
      del p

If one wants to load a project and check some of its properties, it is easy:

::

  >>> from aequilibrae.project import Project

  >>> p = Project('path/to_project')

  # for the modes available in the model
  >>> p.network.modes()
  ['car', 'walk', 'bicycle']

  >>> p.network.count_links()
  157926

  >>> p.network.count_nodes()
  793200


.. _example_usage_paths:

Paths module
------------

::

  from aequilibrae.paths import allOrNothing
  from aequilibrae.paths import path_computation
  from aequilibrae.paths.results import AssignmentResults as asgr
  from aequilibrae.paths.results import PathResults as pthr

Path computation
~~~~~~~~~~~~~~~~

Skimming
~~~~~~~~

Let's suppose you want to compute travel times between all zone on your network. In that case,
you need only a graph that you have previously built, and the list of skims you want to compute.

::

    from aequilibrae.paths.results import SkimResults as skmr
    from aequilibrae.paths import Graph
    from aequilibrae.paths import NetworkSkimming

    # We instantiate the graph and load it from disk (say you created it using the QGIS GUI
    g = Graph()
    g.load_from_disk(aeg_pth)

    # You now have to set the graph for what you want
    # In this case, we are computing fastest path (minimizing free flow time)
    g.set_graph(cost_field='fftime')

    # We are also **blocking** paths from going through centroids
    g.set_blocked_centroid_flows(block_centroid_flows=True)

    # We will be skimming for fftime **AND** distance along the way
    g.set_skimming(['fftime', 'distance'])

    # We instantiate the skim results and prepare it to have results compatible with the graph provided
    result = skmr()
    result.prepare(g)

    # We create the network skimming object and execute it
    # This is multi-threaded, so if the network is too big, prepare for a slow computer
    skm = NetworkSkimming(g, result)
    skm.execute()


If you want to use fewer cores for this computation (which also saves memory), you also can do it
You just need to use the method *set_cores* before you run the skimming. Ideally it is done before preparing it

::

    result = skmr()
    result.set_cores(3)
    result.prepare(g)

And if you want to compute skims between all nodes in the network, all you need to do is to make sure
the list of centroids in your graph is updated to include all nodes in the graph

::

    from aequilibrae.paths.results import SkimResults as skmr
    from aequilibrae.paths import Graph
    from aequilibrae.paths import NetworkSkimming

    g = Graph()
    g.load_from_disk(aeg_pth)

    # Let's keep the original list of centroids in case we want to use it again
    orig_centr = g.centroids

    # Now we set the list of centroids to include all nodes in the network
    g.prepare_graph(g.all_nodes)

    # And continue **almost** like we did before
    # We just need to remember to NOT block paths through centroids. Otherwise there will be no paths available
    g.set_graph(cost_field='fftime', block_centroid_flows=False)
    g.set_skimming('fftime')

    result = skmr()
    result.prepare(g)

    skm = NetworkSkimming(g, result)
    skm.execute()

Setting skimming after setting the graph is **CRITICAL**, and the skim matrices are part of the result object.

You can save the results to your place of choice in AequilibraE format or export to OMX or CSV

::

    result.skims.export('path/to/desired/folder/file_name.omx')

    result.skims.export('path/to/desired/folder/file_name.csv')

    result.skims.copy('path/to/desired/folder/file_name.aem')

.. _comprehensive_traffic_assignment_case:

Traffic assignment
~~~~~~~~~~~~~~~~~~

A simple example of assignment

::

    from aequilibrae.project import Project
    from aequilibrae.paths import TrafficAssignment, TrafficClass
    from aequilibrae.matrix import AequilibraeMatrix

    assig = TrafficAssignment()

    proj = Project('path/to/folder/SiouxFalls.sqlite')
    proj.network.build_graphs()
    # Mode c is car
    car_graph = proj.network.graphs['c']


    mat = AequilibraeMatrix()
    mat.load('path/to/folder/demand.omx')
    # We will only assign one user class stored as 'matrix' inside the OMX file
    mat.computational_view(['matrix'])

    # Creates the assignment class
    assigclass = TrafficClass(g, mat)

    # If you want to know which assignment algorithms are available:
    assig.algorithms_available()

    # If you want to know which Volume-Delay functions are available
    assig.vdf.functions_available()

    # The first thing to do is to add at list of traffic classes to be assigned
    assig.set_classes([assigclass])

    # Then we set the volume delay function
    assig.set_vdf("BPR")  # This is not case-sensitive

    # And its parameters
    assig.set_vdf_parameters({"alpha": "alpha", "beta": "beta"})

    # If you don't have parameters in the network, but rather global ones
    # assig.set_vdf_parameters({"alpha": 0.15, "beta": 4})

    # The capacity and free flow travel times as they exist in the graph
    assig.set_capacity_field("capacity")
    assig.set_time_field("free_flow_time")

    # And the algorithm we want to use to assign
    assig.set_algorithm('bfw')

    # To overwrite the number of iterations and the relative gap intended
    assig.max_iter = 250
    assig.rgap_target = 0.0001

    # To overwrite the number of CPU cores to be used
    assig.set_cores(3)

    # we then execute the assignment
    assig.execute()

Assigning traffic on TNTP instances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There is a set of well known traffic assignment problems used in the literature
maintained on `GitHub <https://github.com/bstabler/TransportationNetworks/>`_
that is often used for tests, so we will use one of those problems here.

Let's suppose we want to perform traffic assignment for one of those problems
and check the results against the reference results.

The parsing and importing of those networks are not really the case here, but
there is `online code <https://gist.github.com/pedrocamargo/d565f545667fd473ea0590c7866965de>`_
available for doing that work.

::

    import os
    import sys
    import numpy as np
    import pandas as pd
    from aequilibrae.paths import TrafficAssignment
    from aequilibrae.paths import Graph
    from aequilibrae.paths.traffic_class import TrafficClass
    from aequilibrae.matrix import AequilibraeMatrix, AequilibraeData
    import matplotlib.pyplot as plt

    from aequilibrae import logger
    import logging

    # We redirect the logging output to the terminal
    stdout_handler = logging.StreamHandler(sys.stdout)
    logger.addHandler(stdout_handler)

    # Let's work with Sioux Falls
    os.chdir('D:/src/TransportationNetworks/SiouxFalls')
    result_file = 'SiouxFalls_flow.tntp'

    # Loads and prepares the graph
    g = Graph()
    g.load_from_disk('graph.aeg')
    g.set_graph('time')
    g.cost = np.array(g.cost, copy=True)
    g.set_skimming(['time'])
    g.set_blocked_centroid_flows(True)

    # Loads and prepares the matrix
    mat = AequilibraeMatrix()
    mat.load('demand.aem')
    mat.computational_view(['matrix'])

    # Creates the assignment class
    assigclass = TrafficClass(g, mat)

    # Instantiates the traffic assignment problem
    assig = TrafficAssignment()

    # configures it properly
    assig.set_vdf('BPR')
    assig.set_vdf_parameters(**{'alpha': 0.15, 'beta': 4.0})
    assig.set_capacity_field('capacity')
    assig.set_time_field('time')
    assig.set_classes(assigclass)
    # could be assig.set_algorithm('frank-wolfe')
    assig.set_algorithm('msa')

    # Execute the assignment
    assig.execute()

    # the results are within each traffic class only one, in this case
    assigclass.results.link_loads

.. _multiple_user_classes:

Setting multiple user classes before assignment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Let's suppose one wants to setup a matrix for assignment that has two user
classes, *red_cars* and *blue cars* for a single traffic class. To do that, one
needs only to call the *computational_view* method with a list of the two
matrices of interest.  Both matrices need to be contained in the same file (and
to be contiguous if an *.aem instead of a *.omx file) however.

::

    mat = AequilibraeMatrix()
    mat.load('demand.aem')
    mat.computational_view(['red_cars', 'blue_cars'])


Advanced usage: Building a Graph
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Let's suppose now that you are interested in creating links from a bespoke procedure. For
the purpose of this example, let's say you have a sparse matrix representing a graph as
an adjacency matrix

::

    from aequilibrae.paths import Graph
    from aequilibrae.project.network import Network
    from scipy.sparse import coo_matrix

    # original_adjacency_matrix is a sparse matrix where positive values are actual links
    # where the value of the cell is the distance in that link

    # We create the sparse matrix in proper sparse matrix format
    sparse_graph = coo_matrix(original_adjacency_matrix)

    # We create the structure to create the network
    all_types = [k._Graph__integer_type,
                 k._Graph__integer_type,
                 k._Graph__integer_type,
                 np.int8,
                 k._Graph__float_type,
                 k._Graph__float_type]

    # List of all required link fields for a network
    # Network.req_link_flds

    # List of all required node fields for a network
    # Network.req_node_flds

    # List of fields that are reserved for internal workings
    # Network.protected_fields

    dt = [(t, d) for t, d in zip(all_titles, all_types)]

    # Number of links
    num_links = sparse_graph.data.shape[0]

    my_graph = Graph()
    my_graph.network = np.zeros(links, dtype=dt)

    my_graph.network['link_id'] = np.arange(links) + 1
    my_graph.network['a_node'] = sparse_graph.row
    my_graph.network['b_node'] = sparse_graph.col
    my_graph.network["distance"] = sparse_graph.data

    # If the links are directed (from A to B), direction is 1. If bi-directional, use zeros
    my_graph.network['direction'] = np.ones(links)

    # Let's say that all nodes in the network are centroids
    list_of_centroids =  np.arange(max(sparse_graph.shape[0], sparse_graph.shape[0])+ 1)
    centroids_list = np.array(list_of_centroids)

    my_graph.type_loaded = 'NETWORK'
    my_graph.status = 'OK'
    my_graph.network_ok = True
    my_graph.prepare_graph(centroids_list)

This usage is really advanced, and very rarely not-necessary. Make sure to know what you are doing
before going down this route

.. _example_usage_distribution:

Trip distribution
-----------------

The support for trip distribution in AequilibraE is not very comprehensive,
mostly because of the loss of relevance that such type of model has suffered
in the last decade.

However, it is possible to calibrate and apply synthetic gravity models and
to perform Iterative Proportional Fitting (IPF) with really high performance,
which might be of use in many applications other than traditional distribution.


.. Synthetic gravity calibration
.. ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. ::

..    some code

Synthetic gravity application
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this example, imagine that you have your demographic information in an
sqlite database and that you have already computed your skim matrix.

It is also important to notice that it is crucial to have consistent data, such
as same set of zones (indices) in both the demographics and the impedance
matrix.

::

    import pandas as pd
    import sqlite3

    from aequilibrae.matrix import AequilibraeMatrix
    from aequilibrae.matrix import AequilibraeData

    from aequilibrae.distribution import SyntheticGravityModel
    from aequilibrae.distribution import GravityApplication


    # We define the model we will use
    model = SyntheticGravityModel()

    # Before adding a parameter to the model, you need to define the model functional form
    model.function = "GAMMA" # "EXPO" or "POWER"

    # Only the parameter(s) applicable to the chosen functional form will have any effect
    model.alpha = 0.1
    model.beta = 0.0001

    # Or you can load the model from a file
    model.load('path/to/model/file')

    # We load the impedance matrix
    matrix = AequilibraeMatrix()
    matrix.load('path/to/impedance_matrix.aem')
    matrix.computational_view(['distance'])

    # We create the vectors we will use
    conn = sqlite3.connect('path/to/demographics/database')
    query = "SELECT zone_id, population, employment FROM demographics;"
    df = pd.read_sql_query(query,conn)

    index = df.zone_id.values[:]
    zones = index.shape[0]

    # You create the vectors you would have
    df = df.assign(production=df.population * 3.0)
    df = df.assign(attraction=df.employment * 4.0)

    # We create the vector database
    args = {"entries": zones, "field_names": ["productions", "attractions"],
        "data_types": [np.float64, np.float64], "memory_mode": True}
    vectors = AequilibraeData()
    vectors.create_empty(**args)

    # Assign the data to the vector object
    vectors.productions[:] = df.production.values[:]
    vectors.attractions[:] = df.attraction.values[:]
    vectors.index[:] = zones[:]

    # Balance the vectors
    vectors.attractions[:] *= vectors.productions.sum() / vectors.attractions.sum()

    args = {"impedance": matrix,
            "rows": vectors,
            "row_field": "productions",
            "model": model,
            "columns": vectors,
            "column_field": "attractions",
            "output": 'path/to/output/matrix.aem',
            "nan_as_zero":True
            }

    gravity = GravityApplication(**args)
    gravity.apply()

Iterative Proportional Fitting (IPF)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The implementation of IPF is fully vectorized and leverages all the speed of NumPy, but it does not include the
fancy multithreading implemented in path computation.

**Please note that the AequilibraE matrix used as input is OVERWRITTEN by the IPF**

::

    import pandas as pd
    from aequilibrae.distribution import Ipf
    from aequilibrae.matrix import AequilibraeMatrix
    from aequilibrae.matrix import AequilibraeData

    matrix = AequilibraeMatrix()

    # Here we can create from OMX or load from an AequilibraE matrix.
    matrix.create_from_omx(path/to/aequilibrae_matrix, path/to/omxfile)

    # The matrix will be operated one (see the note on overwriting), so it does
    # not make sense load an OMX matrix


    source_vectors = pd.read_csv(path/to/CSVs)
    zones = source_vectors.zone.shape[0]

    args = {"entries": zones, "field_names": ["productions", "attractions"],
            "data_types": [np.float64, np.float64], "memory_mode": True}

    vectors = AequilibraEData()
    vectors.create_empty(**args)

    vectors.productions[:] = source_vectors.productions[:]
    vectors.attractions[:] = source_vectors.attractions[:]

    # We assume that the indices would be sorted and that they would match the matrix indices
    vectors.index[:] = source_vectors.zones[:]

    args = {
            "matrix": matrix, "rows": vectors, "row_field": "productions", "columns": vectors,
            "column_field": "attractions", "nan_as_zero": False}

    fratar = Ipf(**args)
    fratar.fit()

    # We can get back to our OMX matrix in the end
    matrix.export(path/to_omx/output)

.. Transit
.. -------
We only have import for now, and it is likely to not work on Windows if you want the geometries

.. _example_usage_transit:

.. GTFS import
.. ~~~~~~~~~~~

.. ::

..    some code

Matrices
--------
Lets say we want to Import the freight matrices provided with FAF into AequilibraE's matrix format
in order to create some Delaunay Lines in QGIS or to perform traffic assignment

Required data
~~~~~~~~~~~~~

* `FAF Matrices <https://faf.ornl.gov/fafweb/Data/FAF4.4_HiLoForecasts.zip>`__
* `Zones System <http://www.census.gov/econ/cfs/AboutGeographyFiles/CFS_AREA_shapefile_010215.zip>`__

Useful Information
~~~~~~~~~~~~~~~~~~

* `FAF overview <https://faf.ornl.gov/fafweb/>`__
* `FAF User Guide <https://faf.ornl.gov/fafweb/data/FAF4%20User%20Guide.pdf>`__
* `The blog post (with data) <http://www.xl-optim.com/matrix-api-and-multi-class-assignment>`__

The code
~~~~~~~~

We import all libraries we will need, including the AequilibraE

::

    import pandas as pd
    import numpy as np
    import os
    from aequilibrae.matrix import AequilibraeMatrix
    from scipy.sparse import coo_matrix

Now we set all the paths for files and parameters we need and import the matrices into a Pandas DataFrame

::

    data_folder = 'Y:/ALL DATA/DATA/Pedro/Professional/Data/USA/FAF/4.4'
    data_file = 'FAF4.4_HiLoForecasts.csv'
    sctg_names_file = 'sctg_codes.csv'  # Simplified to 50 characters, which is AequilibraE's limit
    output_folder = data_folder

    matrices = pd.read_csv(os.path.join(data_folder, data_file), low_memory=False)

We import the sctg codes

::

    sctg_names = pd.read_csv(os.path.join(data_folder, sctg_names_file), low_memory=False)
    sctg_names.set_index('Code', inplace=True)
    sctg_descr = list(sctg_names['Commodity Description'])


We now process the matrices to collect all the data we need, such as:

* List of zones
* CSTG codes
* Matrices/scenarios we are importing

::

    all_zones = np.array(sorted(list(set( list(matrices.dms_orig.unique()) + list(matrices.dms_dest.unique())))))

    # Count them and create a 0-based index
    num_zones = all_zones.shape[0]
    idx = np.arange(num_zones)

    # Creates the indexing dataframes
    origs = pd.DataFrame({"from_index": all_zones, "from":idx})
    dests = pd.DataFrame({"to_index": all_zones, "to":idx})

    # adds the new index columns to the pandas dataframe
    matrices = matrices.merge(origs, left_on='dms_orig', right_on='from_index', how='left')
    matrices = matrices.merge(dests, left_on='dms_dest', right_on='to_index', how='left')

    # Lists sctg codes and all the years/scenarios we have matrices for
    mat_years = [x for x in matrices.columns if 'tons' in x]
    sctg_codes = matrices.sctg2.unique()

We now import one matrix for each year, saving all the SCTG codes as different matrix cores in our zoning system

::

    # aggregate the matrix according to the relevant criteria
    agg_matrix = matrices.groupby(['from', 'to', 'sctg2'])[mat_years].sum()

    # returns the indices
    agg_matrix.reset_index(inplace=True)


    for y in mat_years:
        mat = AequilibraeMatrix()

        # Here it does not make sense to use OMX
        # If one wants to create an OMX from other data sources, openmatrix is
        # the library to use
        kwargs = {'file_name': os.path.join(output_folder, y + '.aem'),
                  'zones': num_zones,
                  'matrix_names': sctg_descr}

        mat.create_empty(**kwargs)
        mat.index[:] = all_zones[:]
        # for all sctg codes
        for i in sctg_names.index:
            prod_name = sctg_names['Commodity Description'][i]
            mat_filtered_sctg = agg_matrix[agg_matrix.sctg2 == i]

            m = coo_matrix((mat_filtered_sctg[y], (mat_filtered_sctg['from'], mat_filtered_sctg['to'])),
                                               shape=(num_zones, num_zones)).toarray().astype(np.float64)

            mat.matrix[prod_name][:,:] = m[:,:]

        mat.close()

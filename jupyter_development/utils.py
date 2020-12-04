import os
import sys

import numpy as np
import pandas as pd

aequ_dir = "/mnt/c/Users/jan.zill/code/aequilibrae"
sys.path.append(aequ_dir)

from aequilibrae.paths import TrafficAssignment  # noqa: E402
from aequilibrae.paths import Graph  # noqa: E402
from aequilibrae.paths.traffic_class import TrafficClass  # noqa: E402
from aequilibrae.matrix import AequilibraeMatrix, AequilibraeData  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

from aequilibrae import logger  # noqa: E402
import logging  # noqa: E402

# We redirect the logging output to the terminal
# stdout_handler = logging.StreamHandler(sys.stdout)
# logger.addHandler(stdout_handler)


def get_gradient_descent_solution(tntp_dir, scenario, link_file, method="bfw", block_centroids=True, rgap=1e-5):
    net = pd.read_csv(os.path.join(tntp_dir, scenario, link_file), skiprows=7, sep="\t")
    net = net.reset_index().rename(columns={"index": "link_id"})

    if scenario == "Anaheim":
        cols_ = ["link_id", "Tail", "Head", "Free Flow Time (min)", "Capacity (veh/h)"]
        col_names = ["link_id", "a_node", "b_node", "time", "capacity"]
    elif scenario == "Berlin-Center":
        cols_ = ["link_id", "Init node ", "Term node ", "Free Flow Time ", "Capacity ", "B ", "Power "]
        col_names = ["link_id", "a_node", "b_node", "time", "capacity", "alpha", "beta"]
    else:
        raise ValueError(f"Scenario {scenario} needs network column name check")

    network = net[cols_]
    network.columns = col_names
    network = network.assign(direction=1)

    g = Graph()
    g.cost = network["time"].values
    g.capacity = network["capacity"].values
    g.free_flow_time = network["time"].values

    g.network = network.to_records(index=False)
    g.network_ok = True
    g.status = "OK"

    # # Loads and prepares the matrix. NOTE: This assumes conversion to aem has been done, Pedro should have a gist online. I also would have that code somewhere.
    mat = AequilibraeMatrix()
    mat.load(os.path.join(tntp_dir, scenario, "demand.aem"))
    mat.computational_view(["matrix"])
    zones = mat.zones
    index = np.arange(zones) + 1

    g.prepare_graph(index)
    g.set_graph("time")
    g.cost = np.array(g.cost, copy=True)
    g.set_skimming(["time"])
    # this might lead to large diffs:
    g.set_blocked_centroid_flows(block_centroids)

    # # Creates the assignment class
    assigclass = TrafficClass(g, mat)

    # Instantiates the traffic assignment problem
    assig = TrafficAssignment()
    assig.set_classes(assigclass)

    # configures it properly
    assig.set_vdf("BPR")
    if scenario == "Anaheim":
        assig.set_vdf_parameters({"alpha": 0.15, "beta": 4.0})
    elif scenario == "Berlin-Center":
        assig.set_vdf_parameters({"alpha": "alpha", "beta": "beta"})
    else:
        raise ValueError(f"Scenario {scenario} needs BPR params")

    assig.set_capacity_field("capacity")
    assig.set_time_field("time")
    # could be assig.set_algorithm('frank-wolfe')
    assig.set_algorithm("bfw")

    assig.rgap_target = rgap

    # Execute the assignment
    assig.execute()

    # the results are within each traffic class only one, in this case
    # assigclass.results.link_loads
    solution = pd.DataFrame(assigclass.graph.network)
    solution["flow"] = assigclass.results.link_loads

    return solution

# distutils: language=c++
# distutils: sources = TrafficAssignment.cpp ShortestPathComputation.cpp

from cpython cimport array
#import array
import ctypes
from libcpp.vector cimport vector

cdef extern from "TrafficAssignment.h":
    ctypedef struct Link:
        int link_id
        float flow
        float t0
        float alfa
        int beta
        int from_node
        int to_node


    cdef cppclass TrafficAssignment:
        TrafficAssignment(unsigned long num_links, unsigned long num_nodes, unsigned long num_centroids) except +
        void insert_od(unsigned long fromnode, unsigned long tonode, float demand)
        void add_link(int link_id, float t0, float alfa, int beta, float capacity, unsigned long from_node,unsigned long to_node)
        void set_edges()
        float get_objective_function()
        void get_subproblem_data(unsigned long origin, float *Q, float *c, float *A, float *b, float *G, float *h)
        unsigned int get_total_paths(int origin)
        unsigned int get_total_paths(int origin, int destination)
        void compute_shortest_paths(int origin)
        void perform_initial_solution()
        void get_link_flows(float *ptr_flows)
        void update_path_flows(unsigned long origin, float *flows)
        void get_odpath_times(int origin, int destination, float *buffer, float *path_times)

        void update_path_flows_without_link_flows(unsigned long origin, float *flows)
        void update_link_flows_stepsize(unsigned long origin, float stepsize)
        void update_all_link_derivatives()
        void update_path_flows_stepsize(unsigned int origin, float stepsize)


cdef class TrafficAssignmentCy:
    cdef TrafficAssignment *thisptr
    cdef object num_nodes
    cdef object num_centroids
    cdef object links

    def __init__(self, links, int num_links, int num_nodes, int num_centroids):
        self.links=links
        self.num_nodes=num_nodes
        self.num_centroids = num_centroids


    def __cinit__(self, links, int num_links, int num_nodes, int num_centroids):
        cdef vector[Link] link_vector
        cdef Link l

        self.thisptr = new TrafficAssignment(num_links, num_nodes, num_centroids)

        for link in links:
            self.thisptr.add_link(link.link_id, link.t0, link.alfa, link.beta, link.capacity, link.node_id_from,
                            link.node_id_to)

        self.thisptr.set_edges()



    def __dealloc__(self):
        del self.thisptr


    def insert_od(self, origin, destination, flow):
        self.thisptr.insert_od(origin, destination, flow)


    def compute_shortest_paths(self, origin):
        self.thisptr.compute_shortest_paths(origin)

    def perform_initial_solution(self):
        self.thisptr.perform_initial_solution()

    def get_link_flows(self):
        zeros = [0.0 for i in range(len(self.links))]
        cdef array.array link_f= array.array('f', zeros)

        self.thisptr.get_link_flows(link_f.data.as_floats)
        return link_f

    def get_objective_function(self):
        return self.thisptr.get_objective_function()


    def get_problem_data(self, origin, num_destinations_from_origin):
        num_paths = self.get_total_paths(origin)

        cdef array.array Q= array.array('f', [0.0 for i in range(num_paths*num_paths)])
        #array.resize(Q,num_paths*num_paths)

        cdef array.array q= array.array('f', [0.0 for i in range(num_paths)])
        #array.resize(q,num_paths)

        cdef array.array A= array.array('f',  [0.0 for i in range(num_destinations_from_origin*num_paths)])
        #array.resize(A, num_destinations_from_origin*num_paths)

        cdef array.array b= array.array('f', [0.0 for i in range(num_destinations_from_origin)])
        #array.resize(b,num_destinations_from_origin)

        cdef array.array G= array.array('f', [0.0 for i in range(num_paths*num_paths)])
        #array.resize(G, num_paths*num_paths)

        cdef array.array h= array.array('f', [0.0 for i in range(num_paths)])
        #array.resize(h,num_paths)

        self.thisptr.get_subproblem_data(origin,Q.data.as_floats,q.data.as_floats,
                                         A.data.as_floats, b.data.as_floats,
                                         G.data.as_floats, h.data.as_floats)

        return Q,q,A,b,G,h


    def get_total_paths(self, origin):
        return self.thisptr.get_total_paths(origin)


    def update_path_flows(self, origin, flows):
        cdef array.array path_flows= array.array('f', flows)
        self.thisptr.update_path_flows(origin, path_flows.data.as_floats)



    #####

    def update_path_flows_without_link_flows(self, origin, flows):
        cdef array.array path_flows = array.array('f', flows)
        self.thisptr.update_path_flows_without_link_flows(origin, path_flows.data.as_floats)

    def update_link_flows_stepsize(self, origin, stepsize):
        self.thisptr.update_link_flows_stepsize(origin, stepsize)

    def update_all_link_derivatives(self):
        self.thisptr.update_all_link_derivatives()

    def update_path_flows_stepsize(self, unsigned int origin, float stepsize):
        self.thisptr.update_path_flows_stepsize(origin, stepsize)

    ######




    def get_path_times(self, origin, destination):
        num_paths = self.thisptr.get_total_paths(origin, destination)

        cdef array.array path_times= array.array('f', [0.0 for i in range(num_paths)])
        cdef array.array path_flows= array.array('f', [0.0 for i in range(num_paths)])

        self.thisptr.get_odpath_times(origin, destination, path_times.data.as_floats, path_flows.data.as_floats)
        return path_times, path_flows



/*
 * TrafficAssignment.cpp
 *
 *  Created on: Dec 20, 2016
 *      Author: fas
 */

#include "TrafficAssignment.h"
#include <memory.h>
#include <math.h>

unsigned int crctab[] = { 0x00000000, 0x04c11db7, 0x09823b6e, 0x0d4326d9, 0x130476dc,
        0x17c56b6b, 0x1a864db2, 0x1e475005, 0x2608edb8, 0x22c9f00f,
        0x2f8ad6d6, 0x2b4bcb61, 0x350c9b64, 0x31cd86d3, 0x3c8ea00a,
        0x384fbdbd, 0x4c11db70, 0x48d0c6c7, 0x4593e01e, 0x4152fda9,
        0x5f15adac, 0x5bd4b01b, 0x569796c2, 0x52568b75, 0x6a1936c8,
        0x6ed82b7f, 0x639b0da6, 0x675a1011, 0x791d4014, 0x7ddc5da3,
        0x709f7b7a, 0x745e66cd, 0x9823b6e0, 0x9ce2ab57, 0x91a18d8e,
        0x95609039, 0x8b27c03c, 0x8fe6dd8b, 0x82a5fb52, 0x8664e6e5,
        0xbe2b5b58, 0xbaea46ef, 0xb7a96036, 0xb3687d81, 0xad2f2d84,
        0xa9ee3033, 0xa4ad16ea, 0xa06c0b5d, 0xd4326d90, 0xd0f37027,
        0xddb056fe, 0xd9714b49, 0xc7361b4c, 0xc3f706fb, 0xceb42022,
        0xca753d95, 0xf23a8028, 0xf6fb9d9f, 0xfbb8bb46, 0xff79a6f1,
        0xe13ef6f4, 0xe5ffeb43, 0xe8bccd9a, 0xec7dd02d, 0x34867077,
        0x30476dc0, 0x3d044b19, 0x39c556ae, 0x278206ab, 0x23431b1c,
        0x2e003dc5, 0x2ac12072, 0x128e9dcf, 0x164f8078, 0x1b0ca6a1,
        0x1fcdbb16, 0x018aeb13, 0x054bf6a4, 0x0808d07d, 0x0cc9cdca,
        0x7897ab07, 0x7c56b6b0, 0x71159069, 0x75d48dde, 0x6b93dddb,
        0x6f52c06c, 0x6211e6b5, 0x66d0fb02, 0x5e9f46bf, 0x5a5e5b08,
        0x571d7dd1, 0x53dc6066, 0x4d9b3063, 0x495a2dd4, 0x44190b0d,
        0x40d816ba, 0xaca5c697, 0xa864db20, 0xa527fdf9, 0xa1e6e04e,
        0xbfa1b04b, 0xbb60adfc, 0xb6238b25, 0xb2e29692, 0x8aad2b2f,
        0x8e6c3698, 0x832f1041, 0x87ee0df6, 0x99a95df3, 0x9d684044,
        0x902b669d, 0x94ea7b2a, 0xe0b41de7, 0xe4750050, 0xe9362689,
        0xedf73b3e, 0xf3b06b3b, 0xf771768c, 0xfa325055, 0xfef34de2,
        0xc6bcf05f, 0xc27dede8, 0xcf3ecb31, 0xcbffd686, 0xd5b88683,
        0xd1799b34, 0xdc3abded, 0xd8fba05a, 0x690ce0ee, 0x6dcdfd59,
        0x608edb80, 0x644fc637, 0x7a089632, 0x7ec98b85, 0x738aad5c,
        0x774bb0eb, 0x4f040d56, 0x4bc510e1, 0x46863638, 0x42472b8f,
        0x5c007b8a, 0x58c1663d, 0x558240e4, 0x51435d53, 0x251d3b9e,
        0x21dc2629, 0x2c9f00f0, 0x285e1d47, 0x36194d42, 0x32d850f5,
        0x3f9b762c, 0x3b5a6b9b, 0x0315d626, 0x07d4cb91, 0x0a97ed48,
        0x0e56f0ff, 0x1011a0fa, 0x14d0bd4d, 0x19939b94, 0x1d528623,
        0xf12f560e, 0xf5ee4bb9, 0xf8ad6d60, 0xfc6c70d7, 0xe22b20d2,
        0xe6ea3d65, 0xeba91bbc, 0xef68060b, 0xd727bbb6, 0xd3e6a601,
        0xdea580d8, 0xda649d6f, 0xc423cd6a, 0xc0e2d0dd, 0xcda1f604,
        0xc960ebb3, 0xbd3e8d7e, 0xb9ff90c9, 0xb4bcb610, 0xb07daba7,
        0xae3afba2, 0xaafbe615, 0xa7b8c0cc, 0xa379dd7b, 0x9b3660c6,
        0x9ff77d71, 0x92b45ba8, 0x9675461f, 0x8832161a, 0x8cf30bad,
        0x81b02d74, 0x857130c3, 0x5d8a9099, 0x594b8d2e, 0x5408abf7,
        0x50c9b640, 0x4e8ee645, 0x4a4ffbf2, 0x470cdd2b, 0x43cdc09c,
        0x7b827d21, 0x7f436096, 0x7200464f, 0x76c15bf8, 0x68860bfd,
        0x6c47164a, 0x61043093, 0x65c52d24, 0x119b4be9, 0x155a565e,
        0x18197087, 0x1cd86d30, 0x029f3d35, 0x065e2082, 0x0b1d065b,
        0x0fdc1bec, 0x3793a651, 0x3352bbe6, 0x3e119d3f, 0x3ad08088,
        0x2497d08d, 0x2056cd3a, 0x2d15ebe3, 0x29d4f654, 0xc5a92679,
        0xc1683bce, 0xcc2b1d17, 0xc8ea00a0, 0xd6ad50a5, 0xd26c4d12,
        0xdf2f6bcb, 0xdbee767c, 0xe3a1cbc1, 0xe760d676, 0xea23f0af,
        0xeee2ed18, 0xf0a5bd1d, 0xf464a0aa, 0xf9278673, 0xfde69bc4,
        0x89b8fd09, 0x8d79e0be, 0x803ac667, 0x84fbdbd0, 0x9abc8bd5,
        0x9e7d9662, 0x933eb0bb, 0x97ffad0c, 0xafb010b1, 0xab710d06,
        0xa6322bdf, 0xa2f33668, 0xbcb4666d, 0xb8757bda, 0xb5365d03,
        0xb1f740b4 };


TrafficAssignment::TrafficAssignment(int num_links, int num_nodes,
				int num_centroids) {
    this->weights = new float[num_links];
    this->costs = new float[num_links];
    n_cent = (unsigned int) num_centroids;
    n_links = (unsigned int) num_links;

	for (unsigned int i=0; i < num_centroids; i++) {
	    Centroid cent;
	    cent.node = i;
	    cent.num_paths=0;

         int *p;
         p = (int*) malloc (num_nodes*num_centroids*PATHS_PER_OD*sizeof(*p) );
         if (p==NULL) {
            std::cout  << "Allocation memory error " << i << std::endl;
         }

         cent.paths = p;
	    //int *p = new int[num_nodes*num_centroids*3]

	    this->centroidsDescriptors.push_back(cent);

	}
	this->num_nodes = num_nodes;
    this->precedence = new int[num_nodes];
    this->buffer_path = new int[num_nodes];
    this->link_flows = new float[num_links];
    this->alphas_1 = new float[num_links];
    this->alphas_2 = new float[num_links];
    this->link_flows_origin = new float[num_links*num_centroids];
    this->link_flows_origin_current_iter_diff = new float[num_links*num_centroids];

    if (link_flows_origin==NULL) {
         std::cout  << "link flow origin allocation failed" <<  std::endl;
    }

    memset(link_flows, 0, sizeof(float)*num_links);
    memset(link_flows_origin, 0, sizeof(float)*num_links*num_centroids);
    memset(link_flows_origin_current_iter_diff, 0, sizeof(float)*num_links*num_centroids);
}


TrafficAssignment::~TrafficAssignment() {
	// TODO Auto-generated destructor stub
}


void TrafficAssignment::insert_od(unsigned long from, unsigned long to, float demand) {
	DestinationDescriptor dest;
	dest.destination = to;
	dest.demand = demand;
	centroidsDescriptors[from].destinationDescriptors[to] = dest;
}

void TrafficAssignment::set_edges() {
	std::vector<int> from_nodes;
	std::vector<int> to_nodes;

	for (int i=0; i < this->links.size(); i++) {
	    from_nodes.push_back(this->links[i].from_node);
	    to_nodes.push_back(this->links[i].to_node);
	}
	this->spComputation = new ShortestPathComputation(num_nodes, this->links.size());
    this->spComputation->set_edges(from_nodes.data(), to_nodes.data());
}


void TrafficAssignment::add_link(int link_id, float t0, float alfa, int beta,
                            float capacity, int from_node, int to_node) {
    Link link;
    link.link_id=link_id;
    link.flow=0;
    link.t0 = t0;
    link.alfa=alfa;
    link.beta=beta;
    link.capacity=capacity;
    link.from_node=from_node;
    link.to_node=to_node;

    this->weights[link_id] = t0;
    this->links.push_back(link);
    /*for(std::vector<Centroid>::iterator it = centroidsDescriptors.begin(); it != centroidsDescriptors.end(); ++it) {
        std::vector<int> paths_on_link;
        it->path_link_incidence[link_id] = paths_on_link;
    }*/
    unsigned long key = (from_node << 16) | to_node;
    node_to_link[key]=link_id;
}


unsigned int TrafficAssignment::get_total_paths(unsigned long origin) {
    return centroidsDescriptors[origin].num_paths;
}


unsigned int TrafficAssignment::get_total_paths(unsigned long origin, unsigned long destination) {
    return centroidsDescriptors[origin].destinationDescriptors[destination].path_indices.size();
}


void TrafficAssignment::perform_initial_solution() {
    for (unsigned int i=0; i< centroidsDescriptors.size(); i++) {
        compute_shortest_paths(i);
        std::map<unsigned long,DestinationDescriptor>::iterator it;
        for (it=centroidsDescriptors[i].destinationDescriptors.begin(); it!=centroidsDescriptors[i].destinationDescriptors.end(); it++)
        {
            centroidsDescriptors[i].path_flows[it->second.path_indices[0]] = it->second.demand;
            //centroidsDescriptors[i].path_flows_current_iter[it->second.path_indices[0]] = 0.0; // Done in compute_shortest_path on first pass
        }
    }
    for (unsigned int i=0; i< centroidsDescriptors.size(); i++) {
        update_link_flows(i);
    }
}


void TrafficAssignment::update_path_flows(unsigned long origin, float *flows) {
    for (unsigned int j=0; j< centroidsDescriptors[origin].path_flows.size();j++) {
        centroidsDescriptors[origin].path_flows[j] = flows[j];
    }
    update_link_flows(origin);
}


void TrafficAssignment::update_link_flows(unsigned int origin) {
    for (unsigned long l_id=0; l_id < links.size();l_id++) {
        float flow=0;
        float previous_flow = link_flows_origin[origin*n_links+l_id];
        float diff=0;

        for (unsigned int j=0; j< centroidsDescriptors[origin].path_link_incidence[l_id].size();j++) {
            flow += centroidsDescriptors[origin].path_flows[centroidsDescriptors[origin].path_link_incidence[l_id][j]];
        }

        diff=flow-previous_flow;
        link_flows[l_id]+=diff;
        update_link_derivatives(l_id);
        link_flows_origin[origin*n_links+l_id]=flow;
    }
}



/******/

// TODO (change): do not want to update path flows here, do that later with alpha. want to store them here? so

// step 3 to calculate new solution
void TrafficAssignment::update_path_flows_without_link_flows(unsigned long origin, float *flows) {
    for (unsigned int j=0; j< centroidsDescriptors[origin].path_flows.size();j++) {
        //centroidsDescriptors[origin].path_flows[j] = flows[j];
        centroidsDescriptors[origin].path_flows_current_iter[j] = flows[j];
    }
    update_link_flows_by_origin(origin);
}


void TrafficAssignment::update_link_flows_by_origin(unsigned int origin) {
    for (unsigned long l_id=0; l_id < links.size(); l_id++) {
        float flow=0;
        for (unsigned int j=0; j< centroidsDescriptors[origin].path_link_incidence[l_id].size();j++) {
            flow += centroidsDescriptors[origin].path_flows_current_iter[centroidsDescriptors[origin].path_link_incidence[l_id][j]];
        }
        float previous_flow = link_flows_origin[origin*n_links+l_id];
        //float diff = flow-previous_flow;
        //link_flows[l_id]+=diff;
        //update_link_derivatives(l_id);
        link_flows_origin_current_iter_diff[origin*n_links+l_id] = flow - previous_flow;
        link_flows_origin[origin*n_links+l_id] = flow; //update to current solution
    }
}

// non-parallel step:
void TrafficAssignment::update_link_flows_stepsize(unsigned int origin, float stepsize) {
    for (unsigned long l_id=0; l_id < links.size();l_id++) {
        link_flows[l_id] += stepsize * link_flows_origin_current_iter_diff[origin*n_links+l_id];
        //update_link_derivatives(l_id);NO, do this once at the end
    }
}

void TrafficAssignment::update_all_link_derivatives() {
    for (unsigned long l_id=0; l_id < links.size();l_id++) {
        update_link_derivatives(l_id);
    }
}


void TrafficAssignment::update_path_flows_stepsize(unsigned int origin, float stepsize) {

    for (unsigned int j=0; j< centroidsDescriptors[origin].path_flows.size();j++) {
        centroidsDescriptors[origin].path_flows[j] = (1.0 - stepsize) * centroidsDescriptors[origin].path_flows[j] +
         stepsize * centroidsDescriptors[origin].path_flows_current_iter[j];
        centroidsDescriptors[origin].path_flows_current_iter[j] = 0.0;
    }
}

/******/






void TrafficAssignment::update_link_derivatives(int link_id) {
    float flow = link_flows[link_id];
    Link l=links[link_id];

    weights[link_id] = l.t0*(1+l.alfa*pow((flow/l.capacity),l.beta));
    float p= pow(flow,l.beta-1);
    float den=pow(l.capacity, l.beta);
    float dtime = p*l.alfa*l.t0*l.beta/den;

    alphas_1[link_id]=dtime/2.0;
    //alphas_2[link_id]=weights[link_id]-flow*alphas_1[link_id];
    alphas_2[link_id]=weights[link_id]-flow*dtime;
}


void TrafficAssignment::compute_shortest_paths(int from_node) {
    this->spComputation->compute_shortest_paths(weights, from_node, precedence, costs);
    std::map<unsigned long,DestinationDescriptor>::iterator it;
    for (it=centroidsDescriptors[from_node].destinationDescriptors.begin(); it!=centroidsDescriptors[from_node].destinationDescriptors.end(); it++)
    {
        compute_path_link_sequence(from_node, it->second.destination);
    }
}


void TrafficAssignment::compute_path_link_sequence(int origin, int destination) {
    unsigned int num_links_path=0;
    int l_id;
    int next_iter = destination;
    unsigned int crc = 0xFFFFFFFF;
    unsigned int byte;

    //std::cout << "for origin: " << origin <<  " ";
    while (next_iter != origin) {
        unsigned long key = (precedence[next_iter] << 16) | next_iter;
        l_id = node_to_link[key];

        buffer_path[num_links_path] = l_id;
        num_links_path++;
        next_iter=precedence[next_iter];
    }
   unsigned int i = 0;
   crc = 0xFFFFFFFF;
   while (i < num_links_path) {
      byte = buffer_path[i];
      crc = (crc >> 8) ^ crctab[(crc ^ byte) & 0xFF];
      i = i + 1;
   }
   crc= ~crc;

   if (this->centroidsDescriptors[origin].crcs.count(crc) == 0) {
        centroidsDescriptors[origin].crcs[crc] = 0;
        unsigned int n_paths = centroidsDescriptors[origin].num_paths;
        memcpy(centroidsDescriptors[origin].paths + n_paths*num_nodes,
        buffer_path, num_links_path*sizeof(int));

        for (i=0; i<num_links_path;i++) {
            //add link to the centroid dictionary
            if (centroidsDescriptors[origin].path_link_incidence.count(buffer_path[i]) == 0) {
                std::vector<unsigned int> vect;
                centroidsDescriptors[origin].path_link_incidence[buffer_path[i]] = vect;
            }
            centroidsDescriptors[origin].path_link_incidence[buffer_path[i]].push_back(n_paths);
        }
        centroidsDescriptors[origin].destinationDescriptors[destination].path_indices.push_back(n_paths);
        centroidsDescriptors[origin].path_flows.push_back(0.0);
        centroidsDescriptors[origin].path_flows_current_iter.push_back(0.0);
        centroidsDescriptors[origin].num_paths += 1;
   }
}


void TrafficAssignment::get_link_flows(float *ptr_flows) {
    memcpy(ptr_flows, link_flows, n_links*sizeof(float));
}


float TrafficAssignment::get_objective_function() {
    float total_cost = 0;
    for (unsigned int link_id=0; link_id < n_links; link_id++) {
        Link l=links[link_id];
        float c_flow = link_flows[link_id];
        total_cost += l.t0*c_flow*(l.alfa*pow((c_flow/l.capacity),l.beta))/(l.beta+1) + l.t0*c_flow;
    }
    return total_cost;
}


void TrafficAssignment::get_subproblem_data(unsigned int origin, float *Q, float *c, float *A, float *b, float *G, float *h) {
    get_objective_data(origin, Q, c);
    get_equality_data(origin, A, b);
    get_inequality_data(origin, G, h);
}


void TrafficAssignment::get_objective_data(unsigned int origin, float *Q, float *c) {
    std::map<int, std::vector<unsigned int> >::iterator it_links;
    std::vector<unsigned int>::iterator it_a;
    std::vector<unsigned int>::iterator it_b;
    int index;
    int num_paths = (int)centroidsDescriptors[origin].num_paths;

    for (it_links=centroidsDescriptors[origin].path_link_incidence.begin(); it_links!=centroidsDescriptors[origin].path_link_incidence.end();it_links++) {
        for (it_a=it_links->second.begin();it_a!=it_links->second.end(); it_a++) {
            for (it_b=it_links->second.begin();it_b!=it_links->second.end(); it_b++) {
                index=num_paths*(*it_a)+(*it_b);
                Q[index] += 2*alphas_1[it_links->first];
            }
            c[*it_a] += 2*alphas_1[it_links->first]*(link_flows[it_links->first]-link_flows_origin[origin*n_links+it_links->first]);
            c[*it_a] += alphas_2[it_links->first];
        }
    }
}


void TrafficAssignment::get_equality_data(unsigned int origin, float *A, float *b) {
    std::map<unsigned long,DestinationDescriptor>::iterator it;
    std::vector<unsigned int>::iterator it_paths;
    int index;
    //unsigned int total_destinations = centroidsDescriptors[origin].destinationDescriptors.size();
    unsigned int num_paths = centroidsDescriptors[origin].num_paths;
    unsigned int destinations_elapsed=0;

    for (it=centroidsDescriptors[origin].destinationDescriptors.begin(); it!=centroidsDescriptors[origin].destinationDescriptors.end(); it++) {
        for (it_paths=it->second.path_indices.begin();it_paths!=it->second.path_indices.end();it_paths++) {
            index=num_paths*(destinations_elapsed)+(*it_paths);
            A[index] = 1.0;
        }
        b[destinations_elapsed] = it->second.demand;
        destinations_elapsed += 1;
    }
}


void TrafficAssignment::get_inequality_data(unsigned int origin, float *G, float *h) {
    unsigned int num_paths = centroidsDescriptors[origin].num_paths;
    int index;
    for (unsigned int i=0; i<num_paths;i++) {
        index=num_paths*i+i;
        G[index] = -1;
        h[i]=0;
    }
}


void TrafficAssignment::get_odpath_times(unsigned long origin, unsigned long destination, float *path_times,
                                         float *path_flows) {
    std::vector<unsigned int>::iterator it_paths;
    unsigned int computed = 0;
    for(it_paths=centroidsDescriptors[origin].destinationDescriptors[destination].path_indices.begin();
        it_paths!=centroidsDescriptors[origin].destinationDescriptors[destination].path_indices.end();
        it_paths++) {

        float path_time=0;
        int start_index=num_nodes*(*it_paths);
        int cur_index=start_index;
        while(true) {
            Link l = links[centroidsDescriptors[origin].paths[cur_index]];
            path_time += weights[l.link_id];
            if (l.from_node == (int)origin) {
                break;
            }
            cur_index +=1;
        }
        path_times[computed] = path_time;
        path_flows[computed] = centroidsDescriptors[origin].path_flows[*it_paths];
        computed++;
    }
}
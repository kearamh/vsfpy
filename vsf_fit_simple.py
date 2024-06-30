import scipy.stats as s
import h5py
import numpy as np
import json
import scipy

# take the fitting function from my other script
from vsf_fit import do_fit

print(scipy.__version__)

# from gatekeep
def unpack_params():

    # retrieve things from pickled params file
    # these are things that don't change in time, so we can get them just once from
    # topmost output before the main loop begins
    # and it doesn't need to happen every loop the way it was before


    with open(curr_root_path + '/params.txt', 'r') as j:
        params = json.loads(j.read())


    # unpacking the params
    level = params['level']
    left_edges = params['left_edges']
    base_dim = params['base_dim']
    x_L= params['x_L']
    val = params['relative_size']
    shape = params['shape']
    samples = params['samples']
    phys = params['physical_size']
    sim_name = params['sim_name']
    
    scale_factor = np.asarray(params['scale_factors'])

    scale_factor = np.insert(scale_factor, 0, 0)

    points = len(scale_factor) - 1

    return level, left_edges, base_dim, x_L, val, shape, samples, phys, sim_name, scale_factor, points

curr_root_path = '/mnt/research/turbulence/hayeskea_vsf/cluster_vsf_test_sanity_check/'

edge_names = ['left', 'right', 'top', 'bottom', 'near', 'far', 'center']
edge_storage = {}
mean_storage = {}

level, left_edges, base_dim, x_L, val, shape, samples, phys, sim_name, scale_factor, points = unpack_params()

q = 'samples_20'

file_in = h5py.File(curr_root_path + str(q) + '.hdf5', 'r') 

keys = list(file_in.keys())

def vsf_binning():

    # for each distance (calculated from scale_factor, perhaps within a tolerance)

        # find the mean velocity for that distance
    
        # save that to an array   

    pass

for k in range(len(keys)):

    ds = keys[k]

    for p in range(len(edge_names)):

        dell = (file_in[ds + '/' + edge_names[p]])[0]

        vel_diff = (file_in[ds + '/' + edge_names[p]])[1]

        print(dell)

        # ### maybe update scipy?
        # ### default number of bins is 10; len_scale_factor or len_scale_factor - 1 creates nans, which break everything
        # ### in fact, any number greater than 10 causes explosions
        # # bin_means, bin_edges, binnumber = s.binned_statistic(dell, vel_diff)
        # bin_means, bin_edges, binnumber = s.binned_statistic(dell, vel_diff, statistic = np.nanmean, bins = num_bins)

        # # print(bin_edges)

        # # bin_edges_pre_cut = bin_edges[1:-1]

        # # ind_remove = np.where(bin_edges_pre_cut == 0)

        # # bin_edges_to_store = bin_edges_pre_cut[np.max(ind_remove), :]

        # edge_storage[edge_names[p]] = bin_edges[1:-1]
        # mean_storage[edge_names[p]] = bin_means[:-1] 

        # print(mean_storage)

    # print(type(mean_storage))

    # do_fit(edge_storage, mean_storage, edge_names, curr_root_path, ds)
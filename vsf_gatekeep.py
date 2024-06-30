"""
Once samples are collected, this script does the actual analysis. It constructs
the VSFs, performs fits on their slopes, and then will correlate between the 
slopes and other features.

The VSF construction starts by loading in the samples from their respective
HDF5 files and merges them into a single file. The samples are then sorted and 
binned by velocity. Since the sampling script, vsf_gaslight, requires that
there be a certain number of points for a predetermined set of distances between
points.

Once the samples are binned, the points that are output can be plotted, or,
alternatively, they can be grouped by region according to the names of the 
boxes. 

These points are also used for fitting and correlation to create correlation
functions.
"""

import numpy as np
import matplotlib.pyplot as plt
from time import process_time
import os
import pickle
import scipy.stats as s
import h5py
import json
import pandas as pd

# take the fitting function from my other script
from vsf_fit import do_fit
from vsf_h5py_merge import h5py_merge
from vsf_tools import read_inputs

# runtime
start = process_time()

# root as in root folder, where the samples are stored
# the batch script which runs this script is an array script, so each
# analysis process is done on its own core

curr_root_path = str(os.environ['curr_root_path'])

print(curr_root_path)

### Creating the dictionaries necessary for all the plotting
combo_edge_storage = {}
combo_mean_storage = {}
edge_storage = {}
mean_storage = {}

# constructs the vsfs from the samples
def do_sort(edge_names, edge_storage, mean_storage, combo_edge_storage, combo_mean_storage):

    # before we can plot we have to load, bin, and organize the samples
    # first for the plots where each box gets its own curve
    for p in range(len(edge_names)):

        print('now storing: ' + edge_names[p])
            
        # retrieve the data from wherever gaslight.py put it
        dell = (file_in[ds + '/' + edge_names[p]])[0]
        vel_diff = (file_in[ds + '/' + edge_names[p]])[1]

        # use binned_statistic to sort the points into bins for plotting
        # this function's bins EXCLUDE the right side and INCLUDE the left, 
        # except for the last "real" bin
        bin_means, bin_edges, binnumber = s.binned_statistic(dell, vel_diff, bins = len(scale_factor))

        # bin_means, bin_edges = np.histogram(a, bins=10, range=None, density=None, weights=None)

        # excluding final bin bc that's the overflow bin
        edge_storage[edge_names[p]] = bin_edges[1:-1]
        mean_storage[edge_names[p]] = bin_means[:-1]

    # and then for the plot where there are curves for combinations of boxes
    if (shape == 'plus') or (shape == 'plus_overlap'):
    
        for q in range(len(sequences)):

            print('now storing: ' + str(sequences[q]))

            dell_combo = np.asarray([])
            vel_diff_combo = np.asarray([])

            for i in range(len(sequences[q])):

                dell = (file_in[ds + '/' + sequences[q][i]])[0]
                vel_diff = (file_in[ds + '/' + sequences[q][i]])[1]

                dell_combo = np.append(dell_combo, dell)
                vel_diff_combo = np.append(vel_diff_combo, vel_diff)

            bin_means, bin_edges, binnumber = s.binned_statistic(dell_combo, vel_diff_combo, bins = scale_factor*x_L*phys)

            combo_edge_storage[seq_names[q]] = bin_edges[1:-1]
            combo_mean_storage[seq_names[q]] = bin_means[:-1]

    else:
        
        combo_edge_storage = None
        combo_mean_storage = None
        
    print('point sorting done')

    return edge_storage, mean_storage, combo_edge_storage, combo_mean_storage

def do_plot(edge_names, edge_storage, mean_storage, combo_edge_storage = None, combo_mean_storage = None):

    # now for the plotting

    # plus-like plots have both the single curves and the combo curves
    if (shape == 'plus') or (shape == 'plus_overlap'):
        fig, (ax0, ax1) = plt.subplots(1, 2, sharey=True, figsize=(22,13))

        for i in edge_names:

            print('now plotting: ' + i)

            # ax0.loglog(edge_storage[i][:-1], mean_storage[i], label = i, linewidth = 3)
            ax0.loglog(edge_storage[i], mean_storage[i], label = i, marker='o', linewidth = 3)

        ax0.set_ylim(1e-1,6e2)

        ### https://www.geeksforgeeks.org/how-to-change-order-of-items-in-matplotlib-legend/
        ### reordering the labels
        handles, labels = ax0.get_legend_handles_labels()
        
        ### specify order
        order = [1,2,3,4,5,6,0]

        ax0.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=4, fancybox=True, shadow=True, fontsize=15,
        handles = [handles[i] for i in order], labels = [labels[i] for i in order])

        ax0.grid()
        ax0.tick_params(axis='both', which='major', labelsize=18)

        for p in seq_names:

            print('now plotting: ' + p)

            ax1.loglog(combo_edge_storage[p], combo_mean_storage[p], label = p, linewidth = 3)

        ax1.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=2, fancybox=True, shadow=True, fontsize=15)
        ax1.grid()
        ax1.tick_params(axis='both', which='major', labelsize=18)

        fig.suptitle(ds + ', ' + str(phys/3) + ' kpc per box', fontsize=24, y = 0.96)
        fig.text(0.5, 0.04, r'$\Delta {l}$  (kpc)', ha='center', fontsize = 20)
        fig.text(0.07, 0.5, r'$\Delta {v}$  (km/s)', va='center', rotation='vertical', fontsize = 20)
        
        fig.text(0.03, 0.04, 't = ' + str(curr_time) + ' Myr', va='center', fontsize = 20)

        fig.savefig(curr_root_path + '/' + ds + '_compare.png')

    # the plotting is a bit simpler for a the cube-like configs since we're not
    # doing the combo plots
    elif (shape == 'cube') or (shape == 'subdivide'):
        fig, ax0 = plt.subplots(figsize=(22,13))   ### this might freak matplotlib out, who knows

        for i in edge_names:

            print('now plotting: ' + i)

            ax0.loglog(edge_storage[i], mean_storage[i], label = i, linewidth = 3)

        ax0.set_ylim(1e-1,6e2)
        ax0.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=4, fancybox=True, shadow=True, fontsize=15)

        ax0.grid()
        ax0.tick_params(axis='both', which='major', labelsize=18)

        fig.suptitle(ds + ', ' + str(phys/3) + ' kpc per box', fontsize=24, y = 0.96)
        fig.text(0.5, 0.04, r'$\Delta {l}$  (kpc)', ha='center', fontsize = 20)
        fig.text(0.07, 0.5, r'$\Delta {v}$  (km/s)', va='center', rotation='vertical', fontsize = 20)
        
        fig.text(0.03, 0.04, 't = ' + str(curr_time) + ' Myr', va='center', fontsize = 20)

        fig.savefig(curr_root_path + '/' + ds + '_compare.png')

    else:
        print('BE AFRAID!!!')

    return

def unpack_params():

    """Retrieve relevant parameters from params file. This code used to use
    pickle for the parameter saving/loading, and that functionality exists
    for those old personal testing samples, but should not be needed for 
    new users."""
    
    try:

        with open(curr_root_path + '/params.txt', 'r') as j:
            params = json.loads(j.read())

    except:
        
        params_in = open(curr_root_path + "/params.pickle","rb")

        unpickler = pickle.Unpickler(params_in)

        params = unpickler.load()

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

def do_init(shape, sim_name):

    """
    Initializes different values necessary for plotting, fitting, and correlation.
    This includes the box name schemes, jet_power retrieval, time array, 
    
    """

    if (shape == 'plus') or (shape == 'plus_overlap'):
        edge_names = ['left', 'right', 'top', 'bottom', 'near', 'far', 'center']
        seq_names = ['lr', 'tb', 'nf', 'all']
        sequences = [['left', 'right'], ['top', 'bottom'], ['near', 'far'], 
                     ['center', 'left', 'right', 'top', 'bottom', 'near', 'far']]

    elif (shape == 'cube') or (shape == 'subdivide'):
        edge_names = ['1', '2', '3', '4', '5', '6', '7', '8']

    else:
        print('The shape entered is not a valid option.')

    times = np.genfromtxt(curr_root_path + '/times.txt')

    # loading the data to be analyzed
    files = os.listdir(curr_root_path)

    if 'parthenon.hst' in files:
        hst = pd.read_csv(curr_root_path + '/parthenon.hst')
        jet_power = hst.iloc[10]

    # The script assumes if not APK, then Enzo. 
    # For jet powers to work with an Enzo simulation, you must produce output
    # logs while the sim runs, then apply my edot_gen.py script to produce
    # a file with the edots isolated. They can then be retrieved here. This is
    # scuffed, I know, but Enzo doesn't seem to have a more intuitive way
    # of recording/retrieving jet powers (for now...)

    # Note 05/08/2024 - below is NOT how this should work; needs fixing
    # else:
    #     ### https://stackoverflow.com/questions/46733052/read-hdf5-file-into-numpy-array
    #     edot = h5py.File('/mnt/home/hayeskea/edots/' + sim_name + '_edot_sorted_cleaned.hd', 'r')
    #     jet_power = edot.get(sim_name + '_edot_sorted_cleaned.hd').value()   # hdf5 to np array
        
    else:
        jet_power = None

    fits = {}

    zeros = np.zeros((len(keys), 5))

    for i in edge_names:

        fits[i] = zeros
    
    if 'seq_names' in locals():
        return edge_names, seq_names, sequences, times, jet_power, fits
    else:
        return edge_names, times, jet_power, fits

###############################################################################

### retrieve samples from their directory

# merge samples into one file; they exist in different files (one for each
# array element used to create them) in order to prevent overwriting
# so now they are merged into one file to be analyzed here
    
# this used to be done at the end of gaslight but is moved here
# to make some other function imports simpler

# adding a check for if the merged files already exists; if so, it is deleted
# and replaced
    
if os.path.exists(curr_root_path + '/samples.hdf5'):

    os.remove(curr_root_path + '/samples.hdf5')

h5py_merge(curr_root_path)

# import the samples
file_in = h5py.File(curr_root_path + '/samples.hdf5', 'r')
keys = list(file_in.keys())

# unpack the parameters
level, left_edges, base_dim, x_L, val, shape, samples, phys, sim_name, scale_factor, points = unpack_params()

# finish initialization, which depends on the shape of the region
if (shape == 'plus') or (shape == 'plus_overlap'):
    edge_names, seq_names, sequences, times, jet_power, fits = do_init(shape, sim_name)
else:
    edge_names, times, jet_power, fits = do_init(shape, sim_name)

### we're finding each output in the hdf5 files
### and then doing operations on each box in each output
### for ds in ts
for k in range(len(keys)):

    try:

        ds = keys[k]

        curr_time = times[k]

        rng = np.random.default_rng()

        print('-------------------------------------')
        print('binning, sorting samples')
        print('-------------------------------------')

        edge_storage, mean_storage, combo_edge_storage, combo_mean_storage = do_sort(edge_names, edge_storage, mean_storage, combo_edge_storage, combo_mean_storage)

        print('-------------------------------------')
        print('plotting vsfs')
        print('-------------------------------------')
        
        do_plot(edge_names, edge_storage, mean_storage, combo_edge_storage, combo_mean_storage)

        plt.clf()

        print('-------------------------------------')
        print('fitting')
        print('-------------------------------------')

        do_fit(edge_storage, mean_storage, edge_names, curr_root_path, ds)

        plt.clf()

        plt.close()
    
    except:
        continue

# print('-------------------------------------')
# print('finding correlations')
# print('-------------------------------------')

# corr_storage = do_corr(fits)

# print('final corr: ', corr_storage)

# with open(root + '/corr.txt', 'w') as corr_file:
#     corr_file.write(json.dumps(corr_storage))

stop = process_time()
print(str(stop - start) + ' seconds elapsed.')
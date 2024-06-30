""" This script is in progress and was not completed enough to be incorporated
into the main code. Its purpose is to correlate different quantities with the
slopes recovered from the fitting routine, but it did not get much past 
initial brainstorming after a previous attempt to write this script was
scarpped. There is not a lot here, and it isn't very unified with the main scripts.
I would suggest starting from scratch here."""

import h5py
import scipy.stats as s
import scipy.signal as sig
import pickle
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

from vsf_fit import do_fit

# something to note: we need the jet power from the .hst file, 
# but the samples from the other directory
path = '/mnt/research/turbulence/hayeskea_vsf/ngc5044_vsf_out_diam150_lvl6/'

# loading the data to be analyzed
files = os.listdir(path)

if 'parthenon.hst' in files:
    hst = pd.read_csv(path + 'parthenon.hst')
    jet_power = hst[:, 10]

params_in = open(path + 'params.pickle',"rb")
unpickler = pickle.Unpickler(params_in)
params = unpickler.load()
scale_factor = np.asarray(params['scale_factors'])
scale_factor = np.insert(scale_factor, 0, 0)

# setting up storage
edge_names = ['left', 'right', 'top', 'bottom', 'near', 'far', 'center']
edge_storage = {}
mean_storage = {}
slope_storage = {}

samples = ['samples_00', 'samples_01', 'samples_02', 'samples_03', 'samples_04', 'samples_05', 'samples_06', 'samples_07', 'samples_08', 'samples_09']

for q in samples:

    file_in = h5py.File(path + str(q) + '.hdf5', 'r') 

    keys = list(file_in.keys())

    for k in range(len(keys)):

        ds = keys[k]

        for p in range(len(edge_names)):

            dell = (file_in[ds + '/' + edge_names[p]])[0]
            vel_diff = (file_in[ds + '/' + edge_names[p]])[1]

            bin_means, bin_edges, binnumber = s.binned_statistic(dell, vel_diff, bins = 30)

            print(bin_edges)

            edge_storage[edge_names[p]] = bin_edges[1:-1]
            mean_storage[edge_names[p]] = bin_means[:-1]

            ### because fitting doesn't do anything across boxes, we can do this step as soon as everything is sorted from a given box
            ### use the actual sort function once this is fully implemented
            slopes = do_fit(edge_storage, mean_storage, edge_names, edge_names(p))

            ### store these all for 
            slope_storage[edge_names[p]]

for p in range(len(edge_names)):

    sig.correlate(jet_power, slope_storage[p])
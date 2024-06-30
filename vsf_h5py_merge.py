import h5py
import glob
import os

def h5py_merge(output):
    # https://stackoverflow.com/questions/58187004/how-can-i-combine-multiple-h5-file/58223603#58223603
    with h5py.File(output + '/samples.hdf5', mode='a') as file_out:
        for h5name in glob.glob(output + '/samples_*.hdf5'):
            file_in = h5py.File(h5name, 'r') 
            for name in file_in:   

                file_in.copy(name, file_out)
    return
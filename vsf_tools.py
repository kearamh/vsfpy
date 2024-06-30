import numpy as np
import os

def clear_prev_outputs(output):

    ### adding this in to make rerunning for testing easier, like in gatekeep
    ### this may be made more robust later to store existing samples elsewhere
    ### to prevent overwriting while allowing new samples
    if os.path.exists(output + '/samples_' + id + '.hdf5'):

        os.remove(output + '/samples_' + id + '.hdf5')

# this function originated in gaslight, but was moved here to be more
# accessible to other scripts
def read_inputs(path_to_input_file):

    """
    In order to get rid of the issue of some variables being imported from the 
    job script, and others being altered within this script, let's just use 
    input files.
    """

    inputs = np.genfromtxt(path_to_input_file,
                    dtype = 'str', delimiter = ' = ', comments = '#')

    keys = inputs[:,0]
    vals = inputs[:,1]

    inputs = dict(zip(keys, vals))

    return inputs
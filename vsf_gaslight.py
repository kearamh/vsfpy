""" This script performs the sampling necessary to create velocity structure 
functions.

The whole simulation area is broken into boxes using the function box_gen. 
These boxes are then used for sampling in parallel, since sampling from the 
whole simulation area at once requires too much memory to be feasible for most
simulations.

These boxes are used by other functions, such as the temp_gen function, 
which applies a mask based on temperature, and do_sampling, which actually 
creates the samples needed to make the structure function.

The function pack_params retrieves certain important values from the simulation, 
such as the size of the full simulation box, the arrangement and dimensions of
the boxes, and other things required by the next script in the analysis pipeline, 
vsf_gatekeep or for organziational/identification purposes.
"""

import yt
import numpy as np
import matplotlib.pyplot as plt
from time import process_time
import os
import json
import re
import h5py

### record when the script starts running
start = process_time()

### setting up rng for later
rng = np.random.default_rng()

### Just in case, we run this to clear out any stray plotting data
plt.clf()

# TODO: think about user-defined left_edges

def box_gen():

    """
    Breaks the simulation domain into smaller boxes according to the sizes 
    provided in the job script (vsf_girlboss) that corresponds with this 
    Python script. There are different arrangements of boxes available.

    The `plus` arrangement is the only one that has been consistently kept up-
    to-date with the rest of the code. Use the others at your own risk.
    """

    shapes = ['plus', 'plus_overlap', 'subdivide', 'cube']

    if shape == 'cube':

        box_val = D/2
        base_dim = np.trunc(box_val/x_L)

        # lower left corner of the cube region
        c = (ds.domain_center.to_value() - box_val)[0]

        left_edges = [[c+box_val, c, c], [c+box_val, c-box_val, c], 
                      [c + box_val, c-box_val, c-box_val], 
                      [c+box_val, c, c-box_val], [c,c,c], [c, c-box_val, c], 
                      [c, c-box_val, c-box_val], [c,c, c-box_val]]

    ### This shape requires information from previous sampling runs, since its
    ### purpose is to compare one set of boxes with another larger set that 
    ### overlaps it for the purpose of comparing the scales of VSFs.
    elif shape == 'plus_overlap':

        old_box_val = old_D/3
        old_base_dim = np.trunc(old_box_val/x_L)

        centers = np.asarray(old_left_edges) + old_box_val/2

        box_val = D/3   # unitary size of a single box
        base_dim = np.trunc(box_val/x_L)

        left_edges = centers - box_val/2

        left_edges = left_edges.tolist()

    # this will need to take in a corner to use, and then should work just like the cube option
    ### breaks up a single box into octants based on input coordinates
    elif shape == 'subdivide':

        box_val = D/2
        base_dim = np.trunc(box_val/x_L)

        # lower left corner of the cube region
        c = corner_choice

        left_edges = [[c+box_val, c, c], [c+box_val, c-box_val, c], 
                      [c + box_val, c-box_val, c-box_val], 
                      [c+box_val, c, c-box_val], [c,c,c], [c, c-box_val, c], 
                      [c, c-box_val, c-box_val], [c,c, c-box_val]]

    ### organize a group of boxes in the shape of a 3d plus sign
    elif shape == 'plus':

        box_val = D/3
        base_dim = np.trunc(box_val/x_L)
        
        ### bottom left corner of the center box; 
        ### everything is relative to this box
        c = (ds.domain_center.to_value() - box_val/2)[0]   

        # ['center', 'left', 'right', 'top', 'bottom', 'near', 'far']
        left_edges = [[c,c,c], [c,c-box_val,c], [c,c+box_val,c], [c,c,c+box_val], 
                      [c,c,c-box_val], [c+box_val,c,c], [c-box_val,c,c]]
        
    else:
        print('The shape \"', shape, 
              '\" is not available. Please choose from the following shapes: ', 
              str(shapes))

    ### there is a loop happening in the bash script that runs this Python script. 
    ### this is done to force "garbage collection" by simply reloading Python
    ### for every box we sample from.
    left_edge = left_edges[next_corner]

    ### create the box based on the features determined from the size inputs
    ### and the shape chosen
    box = ds.arbitrary_grid(left_edge = left_edge, 
                            right_edge = np.asarray(left_edge) + box_val, 
                            dims=[base_dim, base_dim, base_dim])

    return left_edges, left_edge, base_dim, box


def temp_gen():

    """
    Mask simulation outputs by temperature in order to study the behavior of
    gas of a particular temperature range (ex: hot gas vs cold gas).    
    """

    ### This range is a recommendation taken from a conversation with 
    ### Deovrat Prassad, whose simulation data was used extensively 
    ### to help test this code.
    if temp_range == 'cold':
        lower = 0   ### K
        upper = 1e5   ### K

    ### Deovrat specifically cited the "typical Chandra soft x-ray band lower 
    ### temp cut-off and hard X-ray for upper cut-off" to get these values
    elif temp_range == 'hot':
        lower = 5e6   ### K
        upper = 8e7   ### K

    elif type(temp_range) == list:
        lower = temp_range[0]
        upper = temp_range[1]

    ### find all the cells that meet the temperature requirements
    ### when sampling is performed later, only those cells that are marked valid
    ### here will be eligible for sampling in dp_sampling
    temp_arr = ((box["gas", "temperature"].in_units("K") >= lower) 
    & (box["gas", "temperature"].in_units("K") <= upper))

    coords = np.where(temp_arr == 1)
    coords = np.asarray(coords)
    coords = coords.flatten('F')

    rows = int(coords.shape[0]/3)

    coords = np.reshape(coords, (rows, 3))

    return rows, coords


def do_sampling(x_L, base_dim, left_edge, scale_factor, shape, temp_choice):

    """
    This function actually takes the samples which will later be assembled into 
    VSFs.

    The basic sequence of steps is as follows:

    - Two points in space ("vec" and "cen")* are chosen randomly from the 
    simulation domain using NumPy rng. 
    - Vec is normalized.
    - Vec is multiplied by a scaling factor so that all the vectors chosen for 
    this point in the loop are of the same length, ensuring equal sampling across
    relevant length scales.
    - Vec and cen are added together to that we now have a group of vectors with 
    random origins and random pointings, but all with the same length.
    - The difference in velocity between these points is found and recorded.
    
    * The names of these variables comes from the original conception of this 
    scheme, where we imagined "cen" (for "center") to be the center of a sphere 
    and "vec" (for "vector") to be a vector of a random pointing but length 
    equal to the radius of the sphere. If you create many of these spheres, then
    you can find many velocity differences over many separations, thus creating
    a VSF. The names of the variables stuck.
    """

    shape = shape

    vel_diff = []
    dell = []    

    for q in range(len(scale_factor)):
        for p in range(samples):

            if temp_choice == 0:

                ### low = 0 causes norm = 0, which causes everything to explode
                ### produce a random "center"
                cen = rng.integers(low=1, high = base_dim, size = 3)

                ### shoot out a point a fixed distance from that center
                vec = rng.integers(low=1, high = base_dim, size = 3)

            ### if we do care about temp, though, then vec and cen are picked 
            ### from temp_array to ensure all our samples are of the right temp
            else:

                cen = rng.integers(low=1, high = rows, size = 1)
                vec = rng.integers(low=1, high = rows, size = 1)

                cen = coords[cen]
                vec = coords[vec]

                cen = cen[0]
                vec = vec[0]

            norm = np.linalg.norm(vec)

            vec = vec/norm

            vec *= scale_factor[q]

            vec += cen

            vec = vec.astype('int')

            ### gently scoots errant vectors back inside the simulation domain
            if (vec >= base_dim).any():
                ind = np.where(vec >= base_dim)

                over = np.amax(vec[ind]) - base_dim

                vec = vec - over - 1
                cen = cen - over - 1 

            cen = cen.astype('int')
            vec = vec.astype('int')

            ### this is finding the distance between the two points by 
            ### taking the norm of their difference
            dist = np.linalg.norm(vec - cen)*x_L*domain_size_in_kpc
            dell.append(dist)

            ### now we retrieve the actual values at those locations
            ct = box[('gas', 'velocity_magnitude')][cen[0], cen[1], cen[2]]
            vt = box[('gas', 'velocity_magnitude')][vec[0], vec[1], vec[2]]

            # TODO: check apk units
            ### it's in cm/s by default; converting to km/s here
            val1 = ct.to_value()/100000
            val2 = vt.to_value()/100000

            diff = abs(val1 - val2)

            vel_diff.append(diff)

    arr = np.asarray([dell, vel_diff])
    f[hdf_path] = arr

    return


def pack_params():

    """
    Relevant parameters for assembling VSFs from the samples, or for identifying
    samples in a human-readable way are packed into txt.
    """
    
    file_u = str(ds)
    levels_u = level
    rel_size = D
    phys_size = D*domain_size_in_kpc
    samp = samples

    path = output

    col1 = ['output', 'level', 'relative_size', 'physical_size', 'samples',
    'save_directory', 'scale_factors', 'path', 'left_edges', 'base_dim', 'x_L', 
    'shape', 'sim_name']

    col2 = [file_u, levels_u, rel_size, phys_size, samp, output, 
    scale_factor.tolist(), path, left_edges, base_dim, x_L, shape, sim_name]

    params = dict(zip(col1, col2))

    with open(path + '/params.txt', 'w') as p:
        p.write(json.dumps(params))

    return


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


################### now do stuff! ###################

### get inputs from the input file
path_to_input_file = str(os.environ["path_to_input_file"])
inputs = read_inputs(path_to_input_file)

use_prev = int(inputs['use_prev'])
temp_choice = int(inputs['temp_choice'])
temp_range = str(inputs['temp_range'])
shape = str(inputs['shape'])

level_in = int(inputs['level'])
size_in = int(inputs['size'])
points = int(inputs['points'])
samples = int(inputs['samples'])

sim_name = str(inputs['name'])
data_in = str(inputs['data_in'])
output = str(inputs['output'])

if shape == 'subdivide':
    corner_choice = str(inputs['corner_choice'])

### remember, there's a loop running in the bash script to determine what output
### is loaded, and what box is sampled from
next_file = str(os.environ["next_file"])
next_corner = int(os.environ["next_corner"])
id = str(os.environ["id"])

if use_prev == 1:
    prev_params = str(inputs['prev_params'])

if len(id) != 2:
    id = '0' + id

### https://bobbyhadz.com/blog/python-remove-all-non-numeric-characters-from-string
### when you import the array id as a variable, there's some extra stuff attached to it
### which we clean up here
next_file = re.sub(r'[^0-9]', '', next_file)

while len(next_file) != 3:
    next_file = '0' + next_file

# loading the data to be analyzed
files = os.listdir(data_in)
    
### AthenaPK and Enzo have different naming schemes for outputs;
### in addition to that, it seems that athena-based suites do not default
### to cgs when read by yt
### https://yt-project.org/doc/examining/loading_data.html
if 'parthenon.hst' in files:

    # ## units taken from APK input file
    # code_length_cgs = 3.085677580962325e+24 # 1 Mpc in cm
    # code_mass_cgs = 1.98841586e+47          # 1e14 Msun in g
    # code_time_cgs = 3.15576e+16             # 1 Gyr in s

    units_override = {
        "length_unit": (3.085677580962325e+24, "cm"),
        "time_unit": (3.15576e+16, "s"),
        "mass_unit": (1.98841586e+47, "g"),
    }

    ds = yt.load(data_in + '/parthenon.prim.00' + next_file + '.phdf', 
                units_override=units_override)

else:
    ds = yt.load(data_in + '/DD0' + next_file + '/output_0' + next_file)

domain_width = ds.domain_width.in_units("kpc")
domain_size_in_kpc = domain_width[0].to_value()

### INITS 
edge_name_dict = {

    'plus': ['center', 'left', 'right', 'top', 'bottom', 'near', 'far'],
    'plus_overlap': ['center', 'left', 'right', 'top', 'bottom', 'near', 'far'],
    'subdivide': ['1','2','3','4','5','6','7','8'],
    'cube': ['1','2','3','4','5','6','7','8']
}

edge_names = edge_name_dict[shape]

# setting the level of the smaller box divisions
level = level_in

# details related to the sim and the boxes being created in it
# D is the unitary size of the whole region
x_rg = 1/64
x_L = x_rg/(2**level)
D = size_in/domain_size_in_kpc

### allows you to use previous parameters, specifically for the subdivide and 
### plus_overlap cases
if use_prev == 1:

    ### TODO: TEST
    params_in = open(prev_params, "rb")
    params = json.load(params_in)

    old_left_edges = params['left_edges']
    x_L = params['x_L']
    old_D = params['relative_size']
    samples = params['samples']

    ### old_D should be dictated by prev_params
    D = old_D    

left_edges, left_edge, base_dim, box = box_gen()

if temp_choice == 1:

    rows, coords = temp_gen()

stop = base_dim
step = stop/points
stop += step

### amount the vectors are lengthened is based on cells, not physical distance, 
### so the scaling array needs to change with level
scale_factor = np.arange(0,stop,step)  
scale_factor = np.delete(scale_factor, 0)

### this just ensures consistency
points = len(scale_factor)

dirname = str(ds)
dirname = dirname.replace('.','')

f = h5py.File(output + '/samples_' + id + '.hdf5', 'a')

corner = '/' + edge_names[next_corner] + '/'

path = os.path.join(output, dirname + corner)

hdf_path = dirname + corner

### now create the samples and pack up the params
print('-------------------------------------')
print('creating samples')
print('-------------------------------------')

do_sampling(x_L, base_dim, left_edge, scale_factor, shape, temp_choice)

pack_params()

# makes sure that when/if vsf_gatekeep needs access to things in the history 
# file, it has it without needing to deal with the input file
if 'parthenon.hst' in files:
    os.system('cp ' + data_in + '/parthenon.hst ' + output + '/parthenon.hst')

# prints to the output file the time it took to do the sampling
stop = process_time()
print(str(stop - start) + ' seconds elapsed.')
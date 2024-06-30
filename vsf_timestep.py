"""This script simply retrieves the timesteps from the simulation outputs
for the sake of plotting. We do this to avoid having to load simulation outputs
or even yt when we run gatekeep using guillotine."""

import yt
import os

from vsf_tools import read_inputs

# just picked this up from gaslight
path_to_input_file = str(os.environ["path_to_input_file"])
inputs = read_inputs(path_to_input_file)

# get the relevant paths; this used to read directly from the job script
# but now reads from the input file
data_in = str(inputs['data_in'])
path_out = str(inputs['output'])

# loading the data to be analyzed
files = os.listdir(data_in)
    
### AthenaPK and Enzo have different naming schemes for outputs;
if 'parthenon.hst' in files:
    ts = yt.load(data_in + '/parthenon.prim.00???.phdf')

else:
    ts = yt.load(data_in + '/DD0???/output_0???')

times = []

for ds in ts:

    times.append(round(ds.current_time.in_units('Myr').to_value(), 4))

file1 = open(path_out + "/times.txt","w")

for i in times:

    file1.write(str(i))
    file1.write("\n")

file1.close()
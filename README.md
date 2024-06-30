# vsfpy

This is a suite of analysis scripts written for creating velocity structure 
functions (VSFs) from grid-based AMR simulation outputs, such as those produced 
by AthenaPK or Enzo. Included also are various plotting, movie-making, and data 
inspection scripts, tailored to this work.

To run this code, you must be mindful of the version of yt you are using. 

- To run this code on AthenaPK outputs, you must use the version of yt indicated
in the "Data Anaylsis" portion of the AthenaPK GitHub README. This suite also
assumes you are using AthenaPK compiled in the manner demonstrated in the 
group's wiki, which also includes instructions for retrieving and setting up 
the specific environment ("athenapk-env") that was used to make this code work 
with AthenaPK simulation outputs. 

- As of now (June 2024) to run this code on the Enzo simulation ouputs used to 
develop it, some small modifications must be made to your yt install. In 
/yt_source/yt/frontends/enzo/data_structures.py and io.py in that same
directory, every instance of "Active Particles" must be changed to 
"ActiveParticles" (simply removing the space). Yt will not load these outputs 
without this change.

Included in this directory are environments/profiles that are used by the vsf 
jobscripts in order to go between these different yt versions, but any setup 
that you prefer for going between these versions should be easy to incorporate.
As of now, the code does not automatically swap between versions, so you must do
so manually when switching between analyzing Enzo outputs and AthenaPK outputs.

In `job_scripts`, there are job scripts for both regular jobs and for array jobs, 
in case you're starting from 0 and need some examples of job scripts.

In `misc`, there are scripts for making movies from the outputs created by the 
main VSF code, as well as a plotting script for creating yt plots of quantities
such as pressure, temperature and entropy. Included also is a script which
generates edot files for VSF outputs from samples taken from Enzo simulations
in particular, but this script is quite old and likely buggy.

In `sim_stuff`, there are various parameter files for Enzo, as well as one for 
AthenaPK, all in various states of functioning. There is also a cooling table
for Enzo given to me by Deovrat Prassad to be used with the Enzo input files.

In the main directory are all the files related to creating and analyzing VSFs. 
The scripts contained there are as follows: 

- `vsf_corr.py` is what is left of an attempt to write a script that correlates
slopes with other quantities (such as jet power) to try to pull out whatever 
relationship may exist there.

- `vsf_fit.py` is the script which contains the function I wrote for finding the
slopes of the VSFs.

- `vsf_gaslight.py` is the script which does the sampling on the simulation
outputs of your choice.

- `vsf_gatekeep.py` is the script which creates the structure functions from the
samples created by gaslight and performs analysis on these structure functions.

- `vsf_girlboss.sh` is a job script which runs gaslight.

- `vsf_guillotine.sh` is a job script which runs gatekeep.

- `vsf_h5py_merge.py` contains a function for merging individual sample files
into a single file for analysis (see gatekeep for a more detailed explanation 
of the file structure).

- `vsf_timestep.py` creates a separate file containing the timesteps for each
output sh that gatekeep does not need to load yt or the original data.

- `vsf_tools.py` contains various functions uses by the other scripts in this
suite.

This VSF code uses input files to help streamline the process of creating VSFs.
These input files take in a name you choose for the simulation (for example, the
name of the cluster being analyzed), where those outputs can be found, where
samples and plots should be output, details regarding the configuration of how 
you would like the simulation to be sampled (how many points, at what level, over
what size of region, etc). There are also options to use previous outputs to
resample a region with different parameters for the sake of comparison, but
this functionality is old, very likely buggy, and should be treated with a 
healthy amount of skepticism.

To use this code, start with the input file. Fill out the input file as described
above, then go to vsf_girlboss.sh. Ensure that the path to your input file is
set correctly and that your environment is set correctly. Follow the comments in
girlboss to see how to do this. The next thing to consider is parallelization. 
The girlboss script is an array job, and the array IDs are used to break 
simulation runs into groups of 10 outputs. The `SBATCH -a` flag must be set
according to the number of simulation outputs you will be analyzing. For example,
to analyze a sim with 150 outputs, that line would read `SBATCH -a 0-15`. To 
use only outputs 90 - 110 of that run, that line would instead read 
`SBATCH -a 9-11`. Specific paths in girlboss and guillotine will need to be 
changed to reflect your personal setup. Run girlboss to create the samples
that will be turned into VSFs.

To create the VSFs, you will run vsf_guillotine.sh. In this script, ensure the
paths reflect your personal setup, and also be mindful of the array flag, as it 
is also used for parallelization in this script. For example, if you created 3 
sets of samples that you want to analyze using one job script, the paths to 
those samples will need to go into the `root_paths` array in guillotine, and the 
`SBATCH -a` flag must be set to `SBATCH -a 0-2`. Run this script to create and
plot VSFs using the samples created by girlboss. 

There are a few unfinished features related to the analysis script, gatekeep, 
which is run by guillotine. This includes performing linear regression on the
VSFs and creating correlation functions for things like VSF slopes and jet 
power. The fitting script is much farther along than the correlation script, but
neither is complete, so to use these features would require additional effort
from you. Something else to note is that the `binned_statistic` function from 
SciPy seemed to have been broken in the previous version of SciPy that I was
using. Because of the OS update and issues I had updating necessary packages to
get this code up and running again, I am not sure if `binned_statistic` is 
still broken in more recent versions of SciPy, so this is something that will
need to be looked at. Any number of bins other than the default (10) caused this 
function to produce NaNs.

The end of my work on this project coincided with the OS update to Ubuntu, which
means that, in their current state, job scripts are not likely to work and will
need updating for the proper modules. Included in this repository are the original 
environment and modules used to create this suite. Hopefully, these can serve as
a guide for what modules will need to be used to run this code on the new OS.

Happy structure function-ing!

- Keara Hayes
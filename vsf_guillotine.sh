#!/bin/bash --login

# This script is submitted using the 'sbatch' command, i.e., 
#    'sbatch example_batch_script.sb'  (without the quotes).
#
# Look at https://wiki.hpcc.msu.edu/display/ITH/Job+Management+by+SLURM for
# job management commands (to see and modify submitted jobs)

########## SBATCH Lines for Resource Request ##########
#
# See https://slurm.schedmd.com/sbatch.html for a much more complete listing of options.
# 
# See https://docs.nersc.gov/jobs/examples/ for examples of node/task/cpu/etc. configurations
# (and https://help.rc.ufl.edu/doc/Sample_SLURM_Scripts for additional examples)
 
#SBATCH --time=02:30:00             # limit of wall clock time - how long the job will run (same as -t), in format hh:mm:ss
#SBATCH --nodes=1                   # number of different nodes - could be an exact number or a range of nodes (same as -N)
#SBATCH --ntasks=1                # number of tasks - how many tasks (nodes) that you require (same as -n)
#SBATCH --cpus-per-task=1           # number of CPUs (or cores) per task (same as -c)
#SBATCH --mem-per-cpu=4G            # memory required per allocated CPU (or core) - amount of memory (in bytes)
#SBATCH --job-name docu_testing     # you can give your job a name for easier identification (same as -J)
#SBATCH --mail-user=hayeskea@msu.edu   # lists the email address to which emails are sent, with options defined by --mail-type
#SBATCH --mail-type=ALL             # let me know when jobs start, end, or fail.
#SBATCH -a 0

########## Command Lines to Run ##########

#### THE LINES BELOW THIS SET UP THE PYTHON ENVIRONMENT

# unload default Python module
module unload Python

# add in whatever to unload your specific SciPy so this will run

module unload SciPy-bundle/2020.11

# the following two lines set up Python, by modifying
# the Linux environmental variables that will find the Python
# executables and libraries
export PATH=/mnt/home/hayeskea/anaconda3/bin:$PATH
export LD_LIBRARY_PATH=/mnt/home/hayeskea/anaconda3/lib:$LD_LIBRARY_PATH

#### THE LINES BELOW THIS GO TO AND RUN YOUR CODE

# this changes to the directory where your code is located 
cd /mnt/home/hayeskea/structurefunctions/

### If you are plotting more than one set of points at once (ie you have TWO 
### directories because you ran girlboss twice), you will need to make the 
### array (-a) flag relfect this. To analyze two sets of samples, the
### `SBATCH -a` line should read `SBATCH -a 0-1`
root_choice=$SLURM_ARRAY_TASK_ID

root_paths=('/mnt/research/turbulence/hayeskea_vsf/cluster_vsf_test_sanity_check')

curr_root_path=${root_paths[$root_choice]}
export "curr_root_path=$curr_root_path"

# srun vsf_h5py_merge.py

srun python3 vsf_gatekeep.py

# The following lines print out a few lines of simple text, and then system
# information to your batch file output.  This can be useful for debugging.
echo ' '
echo '------------------------------' 
echo ' '
scontrol show job $SLURM_JOB_ID     ### write job information to output file


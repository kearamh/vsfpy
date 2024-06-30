#!/bin/bash --login

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
#SBATCH --job-name documentation_testing     # you can give your job a name for easier identification (same as -J)
#SBATCH --mail-user=hayeskea@msu.edu   # lists the email address to which emails are sent, with options defined by --mail-type
#SBATCH --mail-type=ALL             # let me know when jobs start, end, or fail.
#SBATCH -a 20-21            #arrays
 
########## Command Lines to Run ##########

#### THE LINES BELOW THIS SET UP THE PYTHON ENVIRONMENT

# unload default Python module
module unload Python

# add in whatever to unload your specific SciPy so this will run
module unload SciPy-bundle/2020.11

### Uncomment this line for AthenaPK simulation outputs
source '/mnt/home/hayeskea/environment_load.sh'

### Uncomment these lines for Enzo simulation outputs
# export PATH=/mnt/home/hayeskea/anaconda3/bin:$PATH
# export LD_LIBRARY_PATH=/mnt/home/hayeskea/anaconda3/lib:$LD_LIBRARY_PATH

### THE LINES BELOW THIS GO TO AND RUN YOUR CODE

echo '------------------------------' 
echo "my task id is: $SLURM_ARRAY_TASK_ID"
echo '------------------------------' 

# this changes to the directory where your code is located 
cd /mnt/home/hayeskea/structurefunctions/

export "path_to_input_file=/mnt/home/hayeskea/structurefunctions/input_file.txt"

# this script is equipped to run in parallel
# the way this works is the task id is used to break the simulation outputs into
# groups of 10, and every element of the job array handles one group of 10 outputs
start=$(($SLURM_ARRAY_TASK_ID * 10))
end=$((((1 + $SLURM_ARRAY_TASK_ID) * 10) - 1))

export "id=$SLURM_ARRAY_TASK_ID"

echo "$start"
echo "$end"

for (( c=$start; c<=$end; c++ ))
do
	echo -n "$c "
    export "next_file=$c"

    for i in 0 1 2 3 4 5 6
    do
        export "next_corner=$i"
        srun python3 vsf_gaslight.py
    done
done

srun python3 vsf_timestep.py

# The following lines print out a few lines of simple text, and then system
# information to your batch file output.  This can be useful for debugging.
echo ' '
echo '------------------------------' 
echo ' '
scontrol show job $SLURM_JOB_ID     ### write job information to output file


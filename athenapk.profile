### this is NOT working as of the OS change to Ubuntu.

module purge
module load powertools
module load GCCcore/11.2.0 CMake/3.22.1 git/2.27.0 GCC/11.2.0 Ninja/1.10.2
module load OpenMPI/4.1.1-CUDA-11.8.0 
module load Python/3.9.6

export CMAKE_PREFIX_PATH=/opt/software/HDF5/1.12.1-gompi-2021b:$CMAKE_PREFIX_PATH
export PATH=/opt/software/HDF5/1.12.1-gompi-2021b/bin:$PATH
export LD_LIBRARY_PATH=/opt/software/HDF5/1.12.1-gompi-2021b/lib:$LD_LIBRARY_PATH
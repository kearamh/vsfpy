### This is an attempt at getting the special AthenaPK environment working
### with Ubuntu. This is not working as of 6/25/2024.

module purge
module load powertools/1.2.0
module load CMake/3.18.4-GCCcore-10.2.0 git/2.28.0-GCCcore-10.2.0-nodocs GCC/10.2.0 Ninja/1.10.1-GCCcore-10.2.0
module load OpenMPI/4.0.5-GCC-10.2.0 
module load Python/3.8.6-GCCcore-10.2.0

# export CMAKE_PREFIX_PATH=/opt/software/HDF5/1.12.1-gompi-2021b:$CMAKE_PREFIX_PATH
# export PATH=/opt/software/HDF5/1.12.1-gompi-2021b/bin:$PATH
# export LD_LIBRARY_PATH=/opt/software/HDF5/1.12.1-gompi-2021b/lib:$LD_LIBRARY_PATH
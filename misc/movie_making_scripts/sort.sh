#!/bin/bash

for i in rerun_small_cluster rerun_medium_cluster
do
    for j in density entropy pressure speed temperature vorticity_magnitude
    do
        for k in 200 400 800 1600
		do
			echo $i $j $k
			mkdir $i
			mkdir $i/$j
			mkdir $i/$j/$k
			cp $i"_"$j"_slice_x_output_"*"_"$k"_kpc.png" $i/$j/$k/.
	    
		done
    done
done

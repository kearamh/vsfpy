#!/bin/bash

for i in rerun_small_cluster rerun_medium_cluster
do
    for j in density entropy pressure speed temperature vorticity_magnitude
    do
        for k in 200 400 800 1600
		do
            echo $i $j $k

	    	cd $i/$j/$k

			for l in rerun*png
			do

				convert $l -crop 1084x920+0+0 "crop_"$l
	    	done

	    	ffmpeg -framerate 10 -pattern_type glob -i "crop_*.png" -f mp4 -vcodec h264 -pix_fmt yuv420p -b:v 8M -r 10 $i"_"$j"_slice_x_output_"$k"_kpc.mp4"
	    
	    	cd ../../..
	    
		done
    done
done
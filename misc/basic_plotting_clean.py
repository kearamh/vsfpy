import yt
from yt import derived_field
import os

### yt is easily confused, so if you want to plot entropy, make sure this block runs before anything else

@derived_field(name="entropy", units='K*cm**2/g**(2/3)', sampling_type="cell")
def _entropy(field, data):
     return (data["gas", "temperature"] / (data["gas", "density"])**((5/3)-1))

#############################################################################################

### for each data set, we will plot every quantity, decided by the array ID
plot_choice = int(os.environ["array_in"])

### if you only want to plot one field, you can comment out line 14, and uncomment the line below this
# plot_choice = 4

### this is the path to where you want your plots saved
path = "/mnt/gs21/scratch/hayeskea/plot_test/"

### this list contains the paths to the different datasets you want to plot
sims = ['/mnt/gs21/scratch/hayeskea/rerun_large_cluster/DD0???/output_0???']

### these are the names under which you want the images to be grouped; name 0 goes with sim 0, name 1 with sim 1, etc
### this string will appear in the filename of every image belonging to that simulation
names = ['rerun_large_cluster']

### this is the diameter of the viewing area for the plot
widths = [400, 800, 1600]

def big_ploting():

    for i in range(len(names)):

        name = names[i]
        sim = sims[i]

        ts = yt.load(sim)

        for width in widths:

            if plot_choice == 0:
                # ### temperature

                if name == 'NGC5044':
                    high = 5e+7
                    low = 2e+6

                elif name == 'NGC4472':
                    high = 4e+7
                    low = 2e+6

                elif name == 'rerun_small_cluster':
                    high = 4e+7
                    low = 6e+6

                elif name == 'rerun_medium_cluster':
                    high = 2e+8
                    low = 1e+7                    

                elif name == 'rerun_large_cluster':
                    high = 2e+8
                    low = 1e+7                    

                else:
                    high = 5e+7
                    low = 2e+6

                for ds in ts:
                    try:
                        plot = yt.SlicePlot(ds, "x", ("gas", "temperature"), width=(width, "kpc"))
                        plot.set_zlim('temperature', low, high)
                        plot.set_minorticks("all", True)
                        plot.set_colorbar_minorticks("all", True)
                        plot.annotate_timestamp(redshift=False)
                        plot.annotate_title(name + ', Temperature')
                        plot.save(path + name + '_temperature_slice_x_' + str(ds) + '_' + str(width) + '_kpc.png')
                    except:
                        continue

            if plot_choice == 1:
                ### density

                if name == 'NGC5044':
                    high = 1e-23
                    low = 9e-28

                elif name == 'NGC4472':
                    high = 2e-25
                    low = 4e-28

                elif name == 'rerun_small_cluster':
                    high = 3e-25
                    low = 2e-27

                elif name == 'rerun_medium_cluster':
                    high = 3e-25
                    low = 2e-27

                elif name == 'rerun_large_cluster':
                    high = 6e-25
                    low = 2e-27                                        

                else:
                    high = 1e-23
                    low = 9e-28

                for ds in ts:
                    try:
                        plot = yt.SlicePlot(ds, "x", ("gas", "density"), width=(width, "kpc"))
                        plot.set_zlim('density', low, high)
                        plot.set_minorticks("all", True)
                        plot.set_colorbar_minorticks("all", True)
                        plot.annotate_timestamp(redshift=False)
                        plot.annotate_title(name + ', Density')
                        plot.save(path + name + '_density_slice_x_' + str(ds) + '_' + str(width) + '_kpc.png')
                    except:
                        continue

            if plot_choice == 2:
                ### pressure

                if name == 'NGC5044':
                    high = 4e-9
                    low = 1e-13

                elif name == 'NGC4472':
                    high = 2e-10
                    low = 1e-13

                elif name == 'rerun_small_cluster':
                    high = 2e-10
                    low = 5e-12

                elif name == 'rerun_medium_cluster':
                    high = 5e-10
                    low = 2e-11 

                elif name == 'rerun_large_cluster':
                    high = 2e-9
                    low = 6e-11                                       

                else:
                    high = 4e-9
                    low = 1e-13

                for ds in ts:
                    try:
                        plot = yt.SlicePlot(ds, "x", ("gas", "pressure"), width=(width, "kpc"))
                        plot.set_zlim('pressure', low, high)
                        plot.set_minorticks("all", True)
                        plot.set_colorbar_minorticks("all", True)
                        plot.annotate_timestamp(redshift=False)
                        plot.annotate_title(name + ', Pressure')
                        plot.save(path + name + '_pressure_slice_x_' + str(ds) + '_' + str(width) + '_kpc.png')
                    except:
                        continue

            if plot_choice == 3:
                ### speed

                if name == 'NGC5044':
                    high = 3e5
                    low = 6e1

                elif name == 'NGC4472':
                    high = 3e5
                    low = 8e1

                elif name == 'rerun_small_cluster':
                    high = 3e5
                    low = 2e1          

                elif name == 'rerun_medium_cluster':
                    high = 3e5
                    low = 1e1

                elif name == 'rerun_large_cluster':
                    high = 3e5
                    low = 1e1                                                  

                else:
                    high = 3e5
                    low = 6e1

                for ds in ts:
                    try:
                        plot = yt.SlicePlot(ds, "x", ('gas', 'velocity_magnitude'), width=(width, "kpc"))
                        plot.set_zlim('velocity_magnitude', low, high)
                        plot.set_unit(("gas", "velocity_magnitude"), "km/s")
                        plot.set_minorticks("all", True)
                        plot.set_colorbar_minorticks("all", True)
                        plot.annotate_timestamp(redshift=False)
                        plot.annotate_title(name + ', Velocity Magnitude')
                        plot.save(path + name + '_speed_slice_x_' + str(ds) + '_' + str(width) + '_kpc.png')
                    except:
                        continue

            if plot_choice == 4:
                # ### vorticity

                if name == 'NGC5044':
                    high = 2e-13
                    low = 5e-20

                elif name == 'NGC4472':
                    high = 2e-12
                    low = 2e-19

                elif name == 'rerun_small_cluster':
                    high = 6e-14
                    low = 2e-21     

                elif name == 'rerun_medium_cluster':
                    high = 6e-14
                    low = 6e-21 

                elif name == 'rerun_large_cluster':
                    high = 2e-14
                    low = 9e-21                                                      

                else:
                    high = 2e-13
                    low = 5e-20

                for ds in ts:
                    try:
                        plot = yt.SlicePlot(ds, "x", ('gas', 'vorticity_magnitude'), width=(width, "kpc"))
                        plot.set_zlim('vorticity_magnitude', low, high)
                        plot.set_minorticks("all", True)
                        plot.set_colorbar_minorticks("all", True)
                        plot.annotate_timestamp(redshift=False)
                        plot.annotate_title(name + ', Vorticity Magnitude')
                        plot.save(path + name + '_vorticity_magnitude_slice_x_' + str(ds) + '_' + str(width) + '_kpc.png')
                    except:
                        continue

            if plot_choice == 5: 
                ### entropy

                if name == 'NGC5044':
                    high = 6e26
                    low = 2e24

                elif name == 'NGC4472':
                    high = 1e26
                    low = 1e22

                elif name == 'rerun_small_cluster':
                    high = 1e25
                    low = 1e23

                elif name == 'rerun_medium_cluster':
                    high = 2e26
                    low = 3e23   

                elif name == 'rerun_large_cluster':
                    high = 1e25
                    low = 1e23                                                         

                else:
                    high = 6e26
                    low = 2e24

                for ds in ts:
                    try:
                        plot = yt.SlicePlot(ds, "x",("gas", "entropy"), width=(width, "kpc"))
                        plot.set_zlim('entropy', low, high)
                        plot.set_minorticks("all", True)
                        plot.set_colorbar_minorticks("all", True)
                        plot.annotate_timestamp(redshift=False)
                        plot.annotate_title(name + ', Entropy')
                        plot.save(path + name + '_entropy_slice_x_' + str(ds) + '_' + str(width) + '_kpc.png')
                    except:
                        continue


### I wrote this function so that I could quickly make sample plots for all the 
### fields in order to find appropriate bounds for each field
def test():

    ### bound test ###

    width = 200

    rep_plot = yt.load('/mnt/gs21/scratch/hayeskea/rerun_large_cluster/DD0043/output_0043')

    this_run = 'large'

    plot = yt.SlicePlot(rep_plot, "x", ("gas", "temperature"), width=(width, "kpc"))
    plot.set_minorticks("all", True)
    plot.set_colorbar_minorticks("all", True)
    plot.save(path + 'test/' + this_run + '_temperature')

    plot = yt.SlicePlot(rep_plot, "x", ("gas", "density"), width=(width, "kpc"))
    plot.set_minorticks("all", True)
    plot.set_colorbar_minorticks("all", True)
    plot.save(path + 'test/' + this_run + '_density')

    plot = yt.SlicePlot(rep_plot, "x", ("gas", "pressure"), width=(width, "kpc"))
    plot.set_minorticks("all", True)
    plot.set_colorbar_minorticks("all", True)
    plot.save(path + 'test/' + this_run + '_pressure')

    plot = yt.SlicePlot(rep_plot, "x", ("gas", "velocity_magnitude"), width=(width, "kpc"))
    plot.set_minorticks("all", True)
    plot.set_colorbar_minorticks("all", True)
    plot.save(path + 'test/' + this_run + '_velocity_magnitude')

    plot = yt.SlicePlot(rep_plot, "x", ("gas", "vorticity_magnitude"), width=(width, "kpc"))
    plot.set_minorticks("all", True)
    plot.set_colorbar_minorticks("all", True)
    plot.save(path + 'test/' + this_run + '_vorticity_magnitude')

    plot = yt.SlicePlot(rep_plot, "x", ("gas", "entropy"), width=(width, "kpc"))
    plot.set_minorticks("all", True)
    plot.set_colorbar_minorticks("all", True)
    plot.save(path + 'test/' + this_run + '_entropy')

### just pick which function you want to run and you're off to the races
# test()
big_ploting()
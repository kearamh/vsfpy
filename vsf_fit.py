"""This script contains the function that is meant to fit the curves created by
vsf_gatekeep. This should be working, but progress on incorporating it into
gatekeep was interrupted."""

import scipy.stats as s
import numpy as np
import matplotlib.pyplot as plt
from time import process_time

start = process_time()

def do_fit(edge_storage, mean_storage, edge_names, root, ds):

    """Performs fits on the curves created by vsf_gatekeep. Slopes at each 
    point in the curve are found, then the script runs a t-test to choose if the
    curve is best described by 2 or 3 slopes. This is because what we're trying
    to determine is why Dr. Li and others found steepening in their VSF 
    created from observations. As such, it is useful to determine if there is
    a statistical difference between the slope of the curve on small scales and
    the slope of the curve between that region and where the curve turns over 
    (if the curve of interest does in fact turn over at all)."""

    for m in edge_names:

        turnover = None

        x = np.log10(edge_storage[m])
        y = np.log10(mean_storage[m])

        # start by getting all the slopes and driving scale turnoff;
        # these are the slopes at each point in the curve.

        slopes = np.zeros(len(x))

        slopes[0] = (y[1] - y[0])/(x[1] - x[0])
        slopes[-1] = (y[-1] - y[-2])/(x[-1] - x[-2])

        for i in range(1, len(x) - 1):

            x2 = x[i+1]
            y2 = y[i+1]
            
            x1 = x[i-1]
            y1 = y[i-1]

            slope = (y2 - y1)/(x2 - x1)

            slopes[i] = slope

        plot_ind = np.arange(0, len(slopes), 1)
        plot_ind = np.reshape(plot_ind, (len(slopes), 1))

        for i in range(len(slopes) - 1):

            curr = slopes[i]

            next_slope = slopes[i + 1]

            if (curr >= 0 ) and (next_slope < 0):

                turnover = i

        # set up some bounds; these may need to change if region size has a 
        # large effect. These were chosen by eye and an algorithmic solution
        # is preferred.

        small_scale_lower_bound = 2
        small_scale_upper_bound = 10

        if turnover != None:
            large_scale_lower_bound = turnover + 3

        else:
            large_scale_lower_bound = small_scale_upper_bound + 3
            turnover = small_scale_upper_bound

        # set up the regions
        # there are the main 3 for the 3-slope

        region_00 = slopes[small_scale_lower_bound:turnover]
        region_01 = slopes[small_scale_lower_bound:small_scale_upper_bound]
        region_02 = slopes[small_scale_upper_bound:turnover]
        region_03 = slopes[large_scale_lower_bound:]
        turning_region = slopes[turnover:large_scale_lower_bound]

        ind_00 = plot_ind[small_scale_lower_bound:turnover]
        ind_01 = plot_ind[small_scale_lower_bound:small_scale_upper_bound]
        ind_02 = plot_ind[small_scale_upper_bound:turnover]
        ind_03 = plot_ind[large_scale_lower_bound:]
        ind_turn = plot_ind[turnover:large_scale_lower_bound]

        # this is *not* an average across time; this is the average slope 
        # for each point for a given timestep
        slope_00 = np.average(region_00)
        slope_01 = np.average(region_01)
        slope_02 = np.average(region_02)
        slope_03 = np.average(region_03)

        yints = np.zeros(4)

        yints[0] = y[small_scale_upper_bound] - slope_00 * x[small_scale_upper_bound]
        yints[1] = y[small_scale_upper_bound] - slope_01 * x[small_scale_upper_bound]
        yints[2] = y[turnover] - slope_02 * x[turnover]
        yints[3] = y[-1] - slope_03 * x[-1]

        # gotta bring this data back in to get rid of the logs for the 
        # actual plotting

        x = edge_storage[m]
        y = mean_storage[m]

        line_ref_00 = 10**(yints[0])*x[small_scale_lower_bound:turnover]**slope_00
        line_ref_01 = 10**(yints[1])*x[small_scale_lower_bound:small_scale_upper_bound]**slope_01
        line_ref_02 = 10**(yints[2])*x[small_scale_upper_bound:turnover]**slope_02
        line_ref_03 = 10**(yints[3])*x[large_scale_lower_bound:]**slope_03

        # do a t-test, which is more appropriate than a chisquare test here 
        # because the data are means
        # https://python.plainenglish.io/explaining-p-value-and-its-interpretation-with-examples-in-python-with-chatgpt-acdc8cb55576
        # https://www.scribbr.com/statistics/t-test/

        # do t-test for the 2-slope fit

        # compare what you plot: you drop in the raw data and the calculated line,
        # so those are what you put into the chi-squared calculation
        _, pvalue = s.ttest_ind(y[small_scale_lower_bound:turnover], line_ref_00)

        # null hypothesis: the slopes of the first and second regions are 
        # functionally the same
        
        # if pvalue < 0.1, reject the null hypothesis, fit those regions 
        # separately, and plot the resultant fits
        if pvalue < 0.1:

            slopes = [slope_01, slope_02, slope_03]

            ### this section plots the slopes and their fits
            plt.scatter(ind_01, region_01, c = 'pink')
            plt.scatter(ind_02, region_02, c = 'lightgreen')
            plt.scatter(ind_03, region_03, c = 'lightskyblue')
            plt.scatter(ind_turn, turning_region, c = 'gray')

            plt.axhline(slope_01, c = 'palevioletred')
            plt.axhline(slope_02, c = 'green')
            plt.axhline(slope_03, c = 'royalblue')

            plt.savefig(root + '/fitting_' + str(ds) + '.png')

            plt.clf()

            ### this section plots the data with the lines of best fit
            plt.loglog(x[small_scale_lower_bound:small_scale_upper_bound], y[small_scale_lower_bound:small_scale_upper_bound], marker = 'o', c = 'pink')
            plt.loglog(x[small_scale_upper_bound:turnover], y[small_scale_upper_bound:turnover], marker = 'o', c = 'lightgreen')
            plt.loglog(x[large_scale_lower_bound:], y[large_scale_lower_bound:], marker = 'o', c = 'lightskyblue')
            plt.loglog(x[turnover:large_scale_lower_bound], y[turnover:large_scale_lower_bound], marker = 'o', c = 'gray')

            # plt.ylim(1e-1,6e2)

            plt.loglog(x[small_scale_lower_bound:small_scale_upper_bound], line_ref_01, c = 'palevioletred')
            plt.loglog(x[small_scale_upper_bound:turnover], line_ref_02, c = 'green')
            plt.loglog(x[large_scale_lower_bound:], line_ref_03, c = 'royalblue')
            
            plt.savefig(root + '/ref_plot_' + str(ds) + '.png')

            plt.clf()
        
        # if pvalue greater than or equal to 0.1, there is no evidence against 
        # the null hypothesis; plot the resultant fits
        else:

            slopes = [slope_00, np.nan, slope_03] 

            ### this section plots the slopes and their fits
            plt.scatter(ind_00, region_00, c = 'pink')
            plt.scatter(ind_03, region_03, c = 'plum')
            plt.scatter(ind_turn, turning_region, c = 'gray')

            plt.axhline(slope_00, c = 'palevioletred')
            plt.axhline(slope_03, c = 'indigo')

            plt.savefig(root + '/fitting_' + str(ds) + '.png')

            plt.clf()

            ### this section plots the data with the lines of best fit
            plt.loglog(x[small_scale_lower_bound:turnover], y[small_scale_lower_bound:turnover], marker = 'o', c = 'pink')
            plt.loglog(x[large_scale_lower_bound:], y[large_scale_lower_bound:], marker = 'o', c = 'plum')
            plt.loglog(x[turnover:large_scale_lower_bound], y[turnover:large_scale_lower_bound], marker = 'o', c = 'gray')

            plt.loglog(x[small_scale_lower_bound:turnover], line_ref_00, c = 'palevioletred')
            plt.loglog(x[large_scale_lower_bound:], line_ref_03, c = 'indigo')
            
            plt.savefig(root + '/ref_plot_' + str(ds) + '.png')

            plt.clf()

    return slopes
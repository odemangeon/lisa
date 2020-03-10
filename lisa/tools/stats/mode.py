#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Mode module.

Module which defines the mode statistics functions

@package dr_tools.stats.mode
@ingroup mode

@brief librairie of function to compute the mode of a distribution

@file
@author Olivier Demangeon
@date July 06, 2016
@version 5.2 06/07/2016 ODE # First released version
@todo This module is way to make the statistical_background_estimate function in the background
    estimate module reusable for other purpose. The idea is to remove the statistical_... functions
    from the background estimate module and just call this module in the uniform_bkg_estimate
    function. For that the interfaces of those function needs to be homogenized and the code made
    more general. Work in progress.
"""

from numpy import sqrt, nanpercentile(, histogram, median, where, zeros_like, logical_and, mean


def trimmode(data, bins=None, H_outliers=1, L_outliers=2, debug=False):
    """
    Estimated the mode of trimmed data set.

    Arguments:
    ----------
    data : ndarray
        Data sets
    bins : int or None, optional (None)
        Number of bins for the histogram
    H_outliers : float, optional (2)
        percentage of high value outliers in data
    L_outliers : float, optional (1)
        percentage of low value outliers in data
    debug : Boolean, optional (False)
        If true, output some debugging informations

    Returns:
    --------
    mode : float
        mode of the underlying distribution behind data

    Raises:
    -------
    None
    """
    data_f = data.flatten()
    nb_pix = data.size
    if bins is None:
        bins = "sqrt"
    vmax = nanpercentile((data_f, 100 - H_outliers)
    vmin = nanpercentile((data_f, L_outliers)
    n, x_bins = histogram(data_f, bins=bins, range=(vmin, vmax))
    if debug:
        print("Median number of pixel per bin in the histogram : {}".format(median(n)))
    idx = where(n == n.max())[0][0]
    v_bkg_min = x_bins[idx]
    v_bkg_max = x_bins[idx + 1]
    if debug:
        print("Max value of the mode bin : {} corresponding to {} % of High - low percentile"
              "".format(v_bkg_max, (v_bkg_max - vmin) / (vmax - vmin) * 100))
        print("Min value of the mode bin : {} corresponding to {} % of High - low percentile"
              "".format(v_bkg_min, (v_bkg_min - vmin) / (vmax - vmin) * 100))
    mask_bkg_stat = zeros_like(data)
    mask_bkg_stat[logical_and(data > v_bkg_min, data < v_bkg_max)] = 1
    result = median(data[logical_and(data > v_bkg_min, data < v_bkg_max)])
    # mean(data[logical_and(data>v_bkg_min, data<v_bkg_max)])
    if debug:
        mean_mode = mean(data[logical_and(data > v_bkg_min, data < v_bkg_max)])
        median_mode = median(data[logical_and(data > v_bkg_min, data < v_bkg_max)])
        print("Number of pixels used to compute the backgroound level : {0} corresponding to {1} % "
              "of the image".format(mask_bkg_stat.sum(), mask_bkg_stat.sum()/float(nb_pix)*100))
        print("Mean value of the mode bin : {0} corresponding to {1} % of the max - min values"
              "".format(mean_mode, (mean_mode-vmin)/(vmax-vmin)*100))
        print("Median value of the mode bin : {0} corresponding to {1} % of the max - min values"
              "".format(median_mode, (median_mode-vmin)/(vmax-vmin)*100))
        print("Value of the backrgound estimate : {0} corresponding to {1} % of the max - min "
              "values".format(result, (result-vmin)/(vmax-vmin)*100))
    if debug:
        fig = figure()
        axe1 = fig.add_subplot(3, 3, 1)
        imshow_colorbar(data, ax=axe1, norm=LogNorm())
        axe1.set_title("Input image\n(index = %d)".format(debug_info['index']), size='small')
        axe2 = fig.add_subplot(3, 3, 3)
        imshow_colorbar(mask_bkg_stat, ax=axe2)
        axe2.set_title("Background + stray-light pixels map\n(index = %d)"
                       "".format(debug_info['index']),
                       size='small')
        axe3 = fig.add_subplot(3, 3, 2)
        axe3.hist(data.flatten(), bins=sqrt(nb_pix)/2., cumulative=False,
                  normed=False, log=True, histtype='step')
        axe3.set_title("Histogram of the image\n(index={})".format(debug_info['index']),
                       size='small')
        axe3.set_ylabel("Number of pixels", size='small')
        axe3.set_xlabel("Amplitude [ADU]", size='small')
        ymin, ymax = axe3.get_ylim()
        axe3.vlines(vmin, ymin, ymax, colors='g')
        axe3.vlines(vmax, ymin, ymax, colors='r')
        axe3.text(vmin-100, ymax, "Lth percentile", color='g', horizontalalignment='right',
                  verticalalignment='top', size='small')
        axe3.text(vmax+100, ymax, "Hth percentile", color='r', horizontalalignment='left',
                  verticalalignment='top', size='small')
        axe4 = fig.add_subplot(3, 3, 4)
        axe4.hist(data.flatten(), bins=bins, cumulative=False, normed=False, log=True,
                  histtype='step', range=(vmin, vmax))
        axe4.set_xlim(xmin=vmin-(vmax-vmin)*5./100, xmax=vmax+(vmax-vmin)*5./100)
        axe4.set_title("Histogram of the image between the\nH and L percentiles (index={})"
                       "".format(debug_info['index']), size='small')
        axe4.set_ylabel("Number of pixels", size='small')
        axe4.set_xlabel("Amplitude [ADU]", size='small')
        axe4.vlines(vmin, ymin, ymax, colors='g')
        axe4.vlines(vmax, ymin, ymax, colors='r')
        axe4.text(vmin+10, ymax, "Lth percentile", color='g', horizontalalignment='left',
                  verticalalignment='top', size='small')
        axe4.text(vmax-10, ymax, "Hth percentile", color='r', horizontalalignment='right',
                  verticalalignment='top', size='small')
        axe4.text((vmin+vmax)/2., (ymin+ymax)/2., "Background + Stray-light pixels",
                  horizontalalignment='center', verticalalignment='center', size='small')
        axe5 = fig.add_subplot(3, 3, 5)
        imshow_colorbar(masked_array(data=data, mask=mask_bkg_stat), ax=axe5)
        axe5.set_title("Non background + stray-light pixels\n(index = %d)"
                       "".format(debug_info['index']),
                       size='small')
        axe6 = fig.add_subplot(3, 3, 6)
        imshow_colorbar(masked_array(data=data, mask=logical_not(mask_bkg_stat)), ax=axe6)
        axe6.set_title("Background + stray-light pixels\n(index = %d)"
                       "".format(debug_info['index']), size='small')
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        bottom_spacing = 0.2
        left_right_spacing = 0.05
        fig.text(0.5, bottom_spacing,
                 "Number of bins in the histogram : {0}\n"
                 "(If uniform) Number of pixel per bin : {1}\n"
                 "Max value in the image : {2}\n"
                 "Min value in the image: {3}\n"
                 "High percentile - min value = {4} % of the max - min values\n"
                 "Low percentile - min value = {5} % of the max - min values\n"
                 "Median number of pixel per bin in the histogram : {6}\n"
                 "Max value of the mode bin : {7} corresponding to {8} % of High - low percentile\n"
                 "Min value of the mode bin : {9} corresponding to {10} % of High -"
                 " low percentile\n"
                 "Number of pixels used to compute the backgroound level : {11} corresponding to "
                 "{12} % of the image\n"
                 "Mean value of the mode bin : {13} corresponding to {14} % of the max -"
                 " min values\n"
                 "Median value of the mode bin : {15} corresponding to {16} % of the max - "
                 "min values\n"
                 "Value of the backrgound estimate : {17} corresponding to {18} % of the max "
                 "- min values"
                 "".format(bins,
                           nb_pix/float(bins),
                           max_data,
                           min_data,
                           (vmax-min_data)/(max_data-min_data)*100,
                           (vmin-min_data)/(max_data-min_data)*100,
                           median(n),
                           v_bkg_max, (v_bkg_max-vmin)/(vmax-vmin)*100,
                           v_bkg_min, (v_bkg_min-vmin)/(vmax-vmin)*100,
                           mask_bkg_stat.sum(), mask_bkg_stat.sum()/float(nb_pix)*100,
                           mean_mode, (mean_mode-vmin)/(vmax-vmin)*100,
                           median_mode, (median_mode-vmin)/(vmax-vmin)*100,
                           result, (result-vmin)/(vmax-vmin)*100),
                 size='small',
                 bbox=props,
                 va='center',
                 ha='center',
                 linespacing=0.6)
        fig.subplots_adjust(top=0.95, bottom=bottom_spacing, left=left_right_spacing,
                            right=1-left_right_spacing, wspace=0.2, hspace=0.4)

import numpy as np
import matplotlib.pyplot as pl



#import plot_ttvsimu
#filename='transit_dur_k2_10b.txt'
#plot_ttvsimu.plot_ttvsimu(filename, plotname='test', times='times', duration='duration')


def plot_ttvsimu(filename, plotname=None, times=None, duration=None):
    """
    Plots TTVs and their errors , duration and their errors from the output of ttv_errors


    call:
    plot_ttvsimu.plot_ttvsimu(filename, plotname='test', times=times, duration=duration)

    input:
    filename: output of ttv_errors needed
    plotname: if set then plots are saved to file times with extention _times.png and durations with extention _duration.png
    times: if set then plots TTVs = times - linear fit in minutes
    duration: if set then plots durations in minutes
    can plot both durations and times

    To DO:
    Calculate ephemeris
    """



    timess, etimeslefts , etimesrights, durations, edurlefts, edurrights = np.genfromtxt(filename, unpack=True)
    times = timess.astype("float64")*24.0*60.0
    etimesleft  = etimeslefts.astype("float64")*24.0*60.0
    etimesright =  etimesrights.astype("float64")*24.0*60.0
    duration = durations.astype("float64")*24.0*60.0
    edurleft  = edurlefts.astype("float64")*24.0*60.0
    edurright =  edurrights.astype("float64")*24.0*60.0


    if times is not None:
        N = len(times)

        x = np.arange(0,N,1)
        result = np.polyfit(x, times, 1)

        #print(result)
        pl.errorbar(x, (times-np.polyval(result, x)), yerr=[etimesleft,etimesright] , fmt=".k", capsize=0)
        pl.title("TTVs")
        pl.xlabel("Epoch")
        pl.ylabel("TTVs (min)")
        if plotname is not None:
            pl.savefig(plotname+"_times.png", dpi=150)
            pl.close()
        else:
            pl.show()



    if duration is not None:
        pl.errorbar(x, duration, yerr=[edurleft ,edurright], fmt=".k", capsize=0)
        pl.title("Duration")
        pl.ylabel("Duration (min)")
        pl.xlabel("Epoch")
        if plotname is not None:
            pl.savefig(plotname+"_duration.png", dpi=150)
            pl.close()
        else:
            pl.show()

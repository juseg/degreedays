#!/usr/bin/env python2

import numpy as np
from matplotlib import pyplot as plt
plt.rc('image', cmap='spectral')

def getdata(dataset, region):
    print 'reading netCDF data...'
    from netCDF4 import Dataset

    # open files
    #znc   = Dataset('../data/%s.geop.nc' % dataset)
    lsmnc = Dataset('../data/%s.mask.nc' % dataset)
    ltmnc = Dataset('../data/%s.sat.mon.5801.avg.nc' % dataset)
    stdnc = Dataset('../data/%s.sat.day.5801.dev.monstd.nc' % dataset)

    # read data
    #zvar = znc.variables['z'][0]
    lsm = lsmnc.variables['lsm'][:]
    lon = lsmnc.variables['longitude'][:]
    lat = lsmnc.variables['latitude'][:]
    ltm = ltmnc.variables['t2m'][:] - 273.15
    std = stdnc.variables['t2m'][:]

    # close files
    #znc.close()
    lsmnc.close()
    ltmnc.close()
    stdnc.close()

    # apply mask
    lon, lat = np.meshgrid(lon, lat)
    mask = (lsm == 0)
    if region == 'ant':
        mask += (lat > -60)
    elif region == 'grl':
        mask += (lon - 2*lat > 200) + (2*lon + 3*lat < 800)
    mask = np.tile(mask, (12,1,1))
    ltm = np.ma.masked_where(mask, ltm)
    std = np.ma.masked_where(mask, std)
    return ltm, std

def timeslice(a, month):
    """Extract timeslice from data array"""

    if month == 'all':
        return a[:].mean(axis=0)
    if month == 'djf':
        return a[[12,0,1]].mean(axis=0)
    if month == 'jja':
        return a[6:8].mean(axis=0)
    else:
        return a[int(month)]

def showmap(ltm, std):
    """Show map"""

    plt.subplot(211)
    plt.imshow(ltm)
    plt.subplot(212)
    plt.imshow(std)
    plt.show()


### Command-line interface ###

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset', default='era40')
    parser.add_argument('-r', '--region', default='global')
    parser.add_argument('-m', '--month', default='all')
    parser.add_argument('--showmap', action='store_true')
    args = parser.parse_args()

    ltm, std = getdata(args.dataset, args.region)
    ltm = timeslice(ltm, args.month)
    std = timeslice(std, args.month)
    if args.showmap is not None: showmap(ltm, std)

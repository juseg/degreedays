#!/usr/bin/env python2
# coding: utf-8

import numpy as np
from matplotlib import pyplot as plt
mm = 1 / 25.4
plt.rc('figure', figsize=(85*mm, 65*mm))
plt.rc('figure.subplot', left=9/85., right=83/85., bottom=8/65., top=63/65.)
plt.rc('font', size=6)
plt.rc('image', cmap='spectral')
plt.rc('mathtext', default='regular')
plt.rc('savefig', dpi=254)


### Base functions ###

def _getdata(dataset, region):
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
    mask = np.tile(mask, (12, 1, 1))
    ltm = np.ma.masked_where(mask, ltm)
    std = np.ma.masked_where(mask, std)
    return ltm, std


def _timeslice(a, month):
    """Extract timeslice from data array"""

    if month == 'all':
        return a[:].mean(axis=0)
    if month == 'djf':
        return a[[12, 0, 1]].mean(axis=0)
    if month == 'jja':
        return a[6:8].mean(axis=0)
    else:
        return a[int(month)]


def _savefig(output, png=True, pdf=False):
    print 'saving ' + output
    if png: plt.savefig(output + '.png')
    if pdf: plt.savefig(output + '.pdf')


### Plotting functions ###

def showmap(ltm, std):
    """Show a map of data extent"""

    ltm = _timeslice(ltm, args.month)
    std = _timeslice(std, args.month)
    plt.subplot(211)
    plt.imshow(ltm)
    plt.subplot(212)
    plt.imshow(std)
    plt.show()


def scatter(ltm, std, reg):
    """Annual scatter plot"""

    # plot stdev data
    colors = ['b', 'b', 'g', 'g', 'g', 'r', 'r', 'r', 'y', 'y', 'y', 'b']
    for mon in range(12):
        print 'plotting month %02i data...' % mon
        plt.scatter(ltm[mon], std[mon], marker='+', c=colors[mon], alpha=0.02)

    # add polynomial fit
    if reg == 'grl': bounds = (-45, 10)
    if reg == 'ant': bounds = (-70, 10)
    coef = np.polyfit(ltm.compressed(), std.compressed(), deg=1)
    poly = np.poly1d(coef)
    x = np.arange(*bounds)
    plt.plot(x, poly(x), 'k')
    plt.text(0.1, 0.1, r'$\sigma = %.2f \cdot T + %.2f$' % tuple(coef),
             transform=plt.gca().transAxes)

    # set axes properties and save
    plt.xlabel('Long-term monthly mean')
    plt.ylabel('Long-term monthly standard deviation')
    plt.xlim(*bounds)
    _savefig('stdev-param-scatter-%s' % args.region)


### Command-line interface ###

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset', default='era40')
    parser.add_argument('-r', '--region', default='grl')
    parser.add_argument('-m', '--month', default='all')
    parser.add_argument('--showmap', action='store_true', help=showmap.__doc__)
    parser.add_argument('--scatter', action='store_true', help=scatter.__doc__)
    args = parser.parse_args()

    ltm, std = _getdata(args.dataset, args.region)
    if args.scatter: scatter(ltm, std, args.region)
    if args.showmap: showmap(ltm, std)

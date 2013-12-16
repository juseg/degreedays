#!/usr/bin/env python2
# coding: utf-8

import cartopy.crs as ccrs
import iris
import iris.coord_categorisation
import iris.plot as iplt
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

def _getdata(dat, reg, mon):

    # open files
    print 'reading netCDF data...'
    #z   = iris.load_cube('../data/%s.geop.nc' % dat)
    lsm = iris.load_cube('../data/%s.mask.nc' % dat)
    ltm = iris.load_cube('../data/%s.sat.mon.5801.avg.nc' % dat)
    std = iris.load_cube('../data/%s.sat.day.5801.dev.monstd.nc' % dat)
    ltm.convert_units('degC')

    # apply regional mask
    mask = (lsm.data[0] == 0)
    lon = lsm.coord('longitude').points
    lat = lsm.coord('latitude').points
    lon, lat = np.meshgrid(lon, lat)
    if reg == 'ant':
        mask += (lat > -60)
    elif reg == 'grl':
        mask += (lon - 2*lat > 200) + (2*lon + 3*lat < 800)
    mask = np.tile(mask, (12, 1, 1))
    ltm.data = np.ma.masked_where(mask, ltm.data)
    std.data = np.ma.masked_where(mask, std.data)

    # extract monthly timeslice
    if mon == 'all':
        return ltm, std
    elif mon == 'avg':
        aggregator = iris.analysis.MEAN
        return (cube.collapsed('time', aggregator) for cube in (ltm, std))
    elif mon in ('djf', 'mam', 'jja', 'son'):
        for cube in ltm, std:
            iris.coord_categorisation.add_season(cube, 'time', name='season')
        return (cube.aggregated_by('season', iris.analysis.MEAN)
                .extract(iris.Constraint(season=mon))
                for cube in (ltm, std))
    else:
        return (cube[int(mon)] for cube in (ltm, std))


def _savefig(output, png=True, pdf=False):
    print 'saving ' + output
    if png: plt.savefig(output + '.png')
    if pdf: plt.savefig(output + '.pdf')


### Plotting functions ###

def drawmap(ltm, std):
    """Plot data on a map"""

    # initialize figure
    proj = ccrs.PlateCarree()
    figw, figh = 85., 72.
    fig = plt.figure(figsize=(figw*mm, figh*mm))

    # plot monthly means
    ax = plt.axes([2/figw, 37/figh, 66/figw, 33/figh], projection=proj)
    cs = iplt.contourf(ltm)
    ax = plt.axes([70/figw, 37/figh, 4/figw, 33/figh])
    cb = plt.colorbar(cs, ax)
    cb.set_label('LTM')

    # plot standard deviation
    ax = plt.axes([2/figw, 2/figh, 66/figw, 33/figh], projection=proj)
    cs = iplt.contourf(std)
    ax = plt.axes([70/figw, 2/figh, 4/figw, 33/figh])
    cb = plt.colorbar(cs, ax)
    cb.set_label('STD')


def scatter(ltm, std, reg):
    """Annual scatter plot"""

    # plot stdev data
    colors = ['b', 'b', 'g', 'g', 'g', 'r', 'r', 'r', 'y', 'y', 'y', 'b']
    for mon in range(12):
        print 'plotting month %02i data...' % mon
        plt.scatter(ltm.data[mon], std.data[mon], marker='+', c=colors[mon], alpha=0.02)

    # add polynomial fit
    if reg == 'grl': bounds = (-45, 10)
    if reg == 'ant': bounds = (-70, 10)
    coef = np.polyfit(ltm.data.compressed(), std.data.compressed(), deg=1)
    poly = np.poly1d(coef)
    plt.plot(bounds, poly(bounds), 'k')
    plt.text(0.1, 0.1, r'$\sigma = %.2f \cdot T + %.2f$' % tuple(coef),
             transform=plt.gca().transAxes)

    # set axes properties
    plt.xlabel('Long-term monthly mean')
    plt.ylabel('Long-term monthly standard deviation')
    plt.xlim(*bounds)


### Command-line interface ###

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset', default='era40')
    parser.add_argument('-r', '--region', default='grl')
    parser.add_argument('-m', '--month', default='all')
    parser.add_argument('--map', action='store_true', help=drawmap.__doc__)
    parser.add_argument('--scatter', action='store_true', help=scatter.__doc__)
    args = parser.parse_args()
    dat = args.dataset
    reg = args.region
    mon = args.month

    ltm, std = _getdata(dat, reg, mon)
    if args.scatter:
        scatter(ltm, std, reg)
        _savefig('stdev-param-scatter-%s' % reg)
    if args.map:
        drawmap(ltm, std)
        _savefig('stdev-param-map-%s-%s-%s' % (dat, reg, mon))

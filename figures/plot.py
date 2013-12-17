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

def _load(dat, reg, ann):
    """Load temperature data"""

    # read data files
    lsm = iris.load_cube('../data/%s.mask.nc' % dat)
    ltm = iris.load_cube('../data/%s.sat.mon.5801.avg.nc' % dat)
    std = iris.load_cube('../data/%s.sat.day.5801%s.monstd.nc'
                         % (dat, '' if ann else '.dev'))
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
    return ltm, std


def _extract(cube, mon):
    """Extract time slice from a cube"""

    if mon == 'all':
        return cube
    elif mon == 'avg':
        aggregator = iris.analysis.MEAN
        return cube.collapsed('time', aggregator)
    elif mon in ('djf', 'mam', 'jja', 'son'):
        iris.coord_categorisation.add_season(cube, 'time', name='season')
        return cube.aggregated_by('season', iris.analysis.MEAN).extract(iris.Constraint(season=mon))
    else:
        return cube[int(mon)]


def _savefig(output, png=True, pdf=False):
    print 'saving ' + output
    if png: plt.savefig(output + '.png')
    if pdf: plt.savefig(output + '.pdf')


### Plotting functions ###

def drawmap(ltm, std, dat, reg, mon):
    """Draw maps"""

    # select geographic projection
    if reg == 'grl':
        proj = ccrs.NorthPolarStereo()
        xlim = (-3e6, 0)
        ylim = (-3e6, 0)
    if reg == 'ant':
        proj = ccrs.SouthPolarStereo()
        xlim = (-3e6, 3e6)
        ylim = (-3e6, 3e6)

    # initialize figure
    figw, figh = 86., 56.
    fig = plt.figure(figsize=(figw*mm, figh*mm))

    # plot monthly means
    ax = plt.axes([2/figw, 14/figh, 40/figw, 40/figh], projection=proj)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    levs = np.linspace(-30, 10, 9)
    cs = iplt.contourf(_extract(ltm, mon), levs, extend='both')
    ax = plt.axes([2/figw, 8/figh, 40/figw, 4/figh])
    cb = plt.colorbar(cs, ax, orientation='horizontal')
    cb.set_label('LTM')

    # plot standard deviation
    ax = plt.axes([44/figw, 14/figh, 40/figw, 40/figh],  projection=proj)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    levs = np.linspace(0, 12, 9)
    cs = iplt.contourf(_extract(std, mon), levs, extend='both')
    ax = plt.axes([44/figw, 8/figh, 40/figw, 4/figh])
    cb = plt.colorbar(cs, ax, orientation='horizontal')
    cb.set_label('STD')
    mon = str(mon).zfill(2)
    _savefig('stdev-param-map-%s-%s-%s' % (dat, reg, mon))


def scatter(ltm, std, dat, reg, mon):
    """Draw scatter plots"""

    # list of times
    if mon == 'all': mlist = range(12)
    else: mlist = [mon]

    # plot stdev data
    clist = ['b', 'b', 'g', 'g', 'g', 'r', 'r', 'r', 'y', 'y', 'y', 'b']
    for m in mlist:
        x = _extract(ltm, m).data
        y = _extract(std, m).data
        plt.scatter(x, y, marker='+', c=clist[m], alpha=0.02)

    # add polynomial fit
    if reg == 'grl': bounds = (-45, 10)
    if reg == 'ant': bounds = (-70, 10)
    if mon == 'all':
        coef = np.polyfit(ltm.data.compressed(), std.data.compressed(), deg=1)
        poly = np.poly1d(coef)
        plt.plot(bounds, poly(bounds), 'k')
        plt.text(0.1, 0.1, r'$\sigma = %.2f \cdot T + %.2f$' % tuple(coef),
                 transform=plt.gca().transAxes)

    # set axes properties and save
    plt.xlabel('Long-term monthly mean')
    plt.ylabel('Long-term monthly standard deviation')
    plt.xlim(*bounds)
    plt.ylim(0, 10)
    mon = str(mon).zfill(2)
    _savefig('stdev-param-scatter-%s-%s-%s' % (dat, reg, mon))


### Command-line interface ###

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--annvar', action='store_true',
                        help='Do not remove annual variability')
    parser.add_argument('-d', '--dataset', default='era40')
    parser.add_argument('-r', '--region', default='grl')
    parser.add_argument('--map', action='store_true', help=drawmap.__doc__)
    parser.add_argument('--scatter', action='store_true', help=scatter.__doc__)
    args = parser.parse_args()
    ann = args.annvar
    dat = args.dataset
    reg = args.region

    ltm, std = _load(dat, reg, ann)
    dat = dat + ann*'+ann'
    if args.scatter:
        for mon in range(12)+['all']:
            plt.clf()
            scatter(ltm, std, dat, reg, mon)
    if args.map:
        for mon in range(12):
            plt.clf()
            drawmap(ltm, std, dat, reg, mon)

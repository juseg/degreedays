#!/usr/bin/env python2
# coding: utf-8

import cartopy.crs as ccrs
import iris
import iris.coord_categorisation
import iris.plot as iplt
import numpy as np
from scipy.special import erfc
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap, LogNorm
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
    lon = lsm.coord('longitude').points
    lat = lsm.coord('latitude').points
    lon, lat = np.meshgrid(lon, lat)
    antmask = (lsm.data[0] == 0) + (lat > -60)
    grlmask = (lsm.data[0] == 0) + (lon - 2*lat > 200) + (2*lon + 3*lat < 800)
    for cube in ltm, std:
        cube.data = np.ma.array(cube.data)
        if reg == 'ant':
            cube.data[:,antmask] = np.ma.masked
        elif reg == 'grl':
            cube.data[:,grlmask] = np.ma.masked
        elif reg == 'both':
            cube.data[:,lat<0] = np.roll(cube.data[:,lat<0], 6, axis=0)
            cube.data[:,grlmask*antmask] = np.ma.masked
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
    if reg == 'ant':
        proj = ccrs.SouthPolarStereo()
        xlim = (-3e6, 3e6)
        ylim = (-3e6, 3e6)
    elif reg == 'grl':
        proj = ccrs.NorthPolarStereo()
        xlim = (-3e6, 0)
        ylim = (-3e6, 0)
    elif reg == 'both':
        proj = ccrs.Stereographic()
        xlim = (-40e6, 40e6)
        ylim = (-40e6, 40e6)
    else:
        proj = ccrs.PlateCarree()
        xlim = (-180, 180)
        ylim = (-90, 90)

    # initialize figure
    from matplotlib.colors import Normalize
    figw, figh = 86., 56.
    fig = plt.figure(figsize=(figw*mm, figh*mm))

    # plot monthly means
    ax = plt.axes([2/figw, 14/figh, 40/figw, 40/figh], projection=proj)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    qm = iplt.pcolormesh(_extract(ltm, mon), norm=Normalize(-30, 10))
    ax = plt.axes([2/figw, 8/figh, 40/figw, 4/figh])
    cb = plt.colorbar(qm, ax, extend='both', orientation='horizontal')
    cb.set_label('LTM')

    # plot standard deviation
    ax = plt.axes([44/figw, 14/figh, 40/figw, 40/figh],  projection=proj)
    ax.set_xlim(xlim)
    ax.set_ylim(ylim)
    qm = iplt.pcolormesh(_extract(std, mon), norm=Normalize(0, 12))
    ax = plt.axes([44/figw, 8/figh, 40/figw, 4/figh])
    cb = plt.colorbar(qm, ax, extend='both', orientation='horizontal')
    cb.set_label('STD')
    if type(mon) is int: mon = str(mon+1).zfill(2)
    _savefig('stdev-param-map-%s-%s-%s' % (dat, reg, mon))

def densmap(ltm, std, dat, reg, mon, zoom=False):
    """Draw density maps"""

    # select bounds
    if zoom:
        xmin, xmax, ymin, ymax = -30, 10, 0, 4
    elif reg == 'grl':
        xmin, xmax, ymin, ymax = -45, 10, 0, 10
    else:
        xmin, xmax, ymin, ymax = -70, 10, 0, 10

    # prepare weights
    lon = ltm.coord('longitude').points
    lat = ltm.coord('latitude').points
    dlon = np.radians(lon[1] - lon[0])
    dlat = np.radians(lat[0] - lat[1])
    lon, lat = np.meshgrid(lon, lat)
    x = _extract(ltm, mon).data
    y = _extract(std, mon).data
    if mon == 'all': lat = np.tile(lat, (12, 1, 1))
    lat = np.ma.array(lat, mask=x.mask).compressed()
    weights = 6371**2*np.cos(np.radians(lat))*dlon*dlat

    # plot stdev data
    im = plt.hist2d(x.compressed(), y.compressed(), 100,
                    [[xmin, xmax], [ymin, ymax]],
                    cmap='Blues', weights=weights)[3]

    # plot region of interest
    x = np.arange(xmin, xmax+1., 5.)
    plt.plot(x, np.abs(x/2), 'k', lw=0.2)
    plt.plot(x, np.abs(x), 'k', lw=0.2)
    ytext = 0.8*ymax
    textslope = (xmax-xmin)/(ymax-ymin)*55/74.
    plt.text(-2*ytext, ytext, r'$\sigma = -T/2$',
             rotation=-np.degrees(np.arctan(textslope/2.)))
    plt.text(-ytext, ytext, r'$\sigma = -T$',
             rotation=-np.degrees(np.arctan(textslope)))

    # set axes properties, add colorbar and save
    plt.xlabel('Long-term monthly mean')
    plt.ylabel('Long-term monthly standard deviation')
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)
    cb = plt.colorbar(im)
    if type(mon) is int: mon = str(mon+1).zfill(2)
    _savefig('stdev-param-densmap-%s-%s-%s' % (dat, reg + zoom*'-zoom', mon))


def scatter(ltm, std, dat, reg, mon, zoom=False):
    """Draw scatter plots"""

    # list of times
    if mon == 'all': mlist = range(12)
    else: mlist = [mon]

    # plot stdev data
    clist = ['b', 'b', 'g', 'g', 'g', 'r', 'r', 'r', 'y', 'y', 'y', 'b']
    for m in mlist:
        if reg == 'both':
            lon = ltm.coord('longitude').points
            lat = ltm.coord('latitude').points
            lon, lat = np.meshgrid(lon, lat)
            c = (lat > 0)
        else:
            c = clist[m]
        x = _extract(ltm, m).data
        y = _extract(std, m).data
        plt.scatter(x, y, marker='+', c=c,  alpha=0.02,
                    cmap=ListedColormap(['gray', 'red']))

    # add polynomial fit
    if zoom:
        xmin, xmax, ymin, ymax = -30, 10, 0, 4
    elif reg == 'grl':
        xmin, xmax, ymin, ymax = -45, 10, 0, 10
    else:
        xmin, xmax, ymin, ymax = -70, 10, 0, 10
    if mon == 'all':
        u = ltm.data.compressed() / std.data.compressed()
        coef1 = np.polyfit(ltm.data.compressed(), std.data.compressed(), deg=1)
        coef2 = np.polyfit(ltm.data.compressed(), std.data.compressed(), deg=1,
            w=np.exp(-u**2/2)/np.sqrt(2*np.pi)+u/2*erfc(-u/np.sqrt(2))-(u>0)*u)
        poly1 = np.poly1d(coef1)
        poly2 = np.poly1d(coef2)
        plt.plot((xmin, xmax), poly1((xmin, xmax)), c='gray', ls='--')
        plt.plot((xmin, xmax), poly2((xmin, xmax)), 'k')
        plt.text(0.1, 0.2, r'$\sigma = %.2f \cdot T + %.2f$' % tuple(coef1),
                 color='gray', transform=plt.gca().transAxes)
        plt.text(0.1, 0.1, r'$\sigma = %.2f \cdot T + %.2f$' % tuple(coef2),
                 color='k', transform=plt.gca().transAxes)


    # plot region of interest
    x = np.arange(xmin, xmax+1., 5.)
    plt.plot(x, np.abs(x/2), 'k', lw=0.2)
    plt.plot(x, np.abs(x), 'k', lw=0.2)
    ytext = 0.8*ymax
    textslope = (xmax-xmin)/(ymax-ymin)*55/74.
    plt.text(-2*ytext, ytext, r'$\sigma = -T/2$',
             rotation=-np.degrees(np.arctan(textslope/2.)))
    plt.text(-ytext, ytext, r'$\sigma = -T$',
             rotation=-np.degrees(np.arctan(textslope)))

    # set axes properties and save
    plt.xlabel('Long-term monthly mean')
    plt.ylabel('Long-term monthly standard deviation')
    plt.xlim(xmin, xmax)
    plt.ylim(ymin, ymax)
    if type(mon) is int: mon = str(mon+1).zfill(2)
    _savefig('stdev-param-scatter-%s-%s-%s' % (dat, reg + zoom*'-zoom', mon))


### Command-line interface ###

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--annvar', action='store_true',
                        help='Do not remove annual variability')
    parser.add_argument('-z', '--zoom', action='store_true',
                        help='Zoom on summer values')
    parser.add_argument('-d', '--dataset', default='era40')
    parser.add_argument('-r', '--region', default='grl')
    parser.add_argument('--fig1', action='store_true', help='Draw Fig. 1')
    parser.add_argument('--fig2', action='store_true', help='Draw Fig. 2')
    parser.add_argument('--map', action='store_true', help=drawmap.__doc__)
    parser.add_argument('--densmap', action='store_true', help=densmap.__doc__)
    parser.add_argument('--scatter', action='store_true', help=scatter.__doc__)
    args = parser.parse_args()
    ann = args.annvar
    dat = args.dataset
    reg = args.region

    if args.fig1:
        plt.clf()
        ltm, std = _load('era40', 'both', ann=False)
        scatter(ltm, std, 'era40', 'both', 6, zoom=True)
    if args.fig2:
        plt.clf()
        ltm, std = _load('era40', 'grl', ann=False)
        scatter(ltm, std, 'era40', 'grl', 'all', zoom=False)
    if any((args.densmap, args.scatter, args.map)):
        ltm, std = _load(dat, reg, ann)
        dat = dat + ann*'ann'
        if args.densmap:
            for mon in range(12)+['all']:
                plt.clf()
                densmap(ltm, std, dat, reg, mon, zoom=args.zoom)
        if args.scatter:
            for mon in range(12)+['all']:
                plt.clf()
                scatter(ltm, std, dat, reg, mon, zoom=args.zoom)
        if args.map:
            for mon in range(12):
                plt.clf()
                drawmap(ltm, std, dat, reg, mon)

#!/usr/bin/env python2
# coding: utf-8

import cartopy.crs as ccrs
import iris
import iris.coord_categorisation
import iris.plot as iplt
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap, LogNorm
from mpl_toolkits.mplot3d import axes3d
mm = 1 / 25.4
plt.rc('font', size=6)
plt.rc('image', cmap='spectral')
plt.rc('mathtext', default='regular')
plt.rc('savefig', dpi=254)


### Base functions ###

def _load(dat, reg, ann):
    """Load temperature data"""

    # read data files
    pp = {'era40': 5801, 'erai': 7912}[dat]
    lsm = iris.load_cube('../data/%s.lsm.nc' % dat)
    tvl = iris.load_cube('../data/%s.tvl.nc' % dat)
    ltm = iris.load_cube('../data/%s.sat.mon.%i.avg.nc' % (dat, pp))
    std = iris.load_cube('../data/%s.sat.day.%i%s.monstd.nc'
                         % (dat, pp, '' if ann else '.dev'))
    ltm.convert_units('degC')

    # apply regional mask
    lon = lsm.coord('longitude').points
    lat = lsm.coord('latitude').points
    lon, lat = np.meshgrid(lon, lat)
    icemask = (lsm.data[0] == 0) + (tvl.data[0] > 0)
    antmask = icemask + (lat > -60)
    grlmask = icemask + (lon - 2*lat > 200) + (2*lon + 3*lat < 800) + (lon - 4*lat < -28)
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


def _teffdiff(T, S):
    """Compute sigma effect on effective temperature for melt"""
    from scipy.special import erfc
    u = T / 2.**.5 / S
    return S / 2.**.5 * (np.exp(-u**2)/np.pi**.5 + u*erfc(-u)) - (T>0)*T


def _setxylim(reg, zoom=False):
    """Set axes limits"""
    ax = plt.gca()
    ax.set_xlim((-30. if zoom else -45. if reg == 'grl' else -70.), 10.)
    ax.set_ylim(0., (4. if zoom else 10.))


def _linfit(x, y, w=None, c='k', ls='-', textpos=(0.5, 0.1)):
    """Add linear fit"""
    ax = plt.gca()
    xlim = ax.get_xlim()
    coef = np.polyfit(x, y, deg=1, w=w)
    poly = np.poly1d(coef)
    ax.plot(xlim, poly(xlim), c=c, ls=ls)
    ax.text(*textpos, s=r'$\sigma = %.2f \cdot T + %.2f$' % tuple(coef),
            color=c, transform=ax.transAxes)


def _dteff3d():
    """Plot effective temperature effect in 3D"""
    ax = plt.gca()
    t = np.linspace(-20, 20, 101)
    s = np.linspace(0.001, 10, 101)
    t, s = np.meshgrid(t, s)
    ax.plot_wireframe(t, s, _teffdiff(t, s), rstride=5, cstride=5,
                      color='k', linewidth=0.5)
    ax.set_frame_on=True,
    ax.view_init(45, -105)
    ax.set_zlim(0, 5)
    ax.set_xlabel('T')
    ax.set_ylabel(r'$\sigma$')
    ax.set_zlabel(r'$\Delta T_{eff}$')
    ax.set_zticks(np.arange(0, 6))


def _dteffcontour():
    """Add effective temperature effect contours"""

    # prepare grid
    ax = plt.gca()
    x = np.linspace(*ax.get_xlim(), num=501)
    y = np.linspace(*ax.get_ylim(), num=501)
    x, y = np.meshgrid(x, y)

    # plot tdeff contours
    cs = ax.contour(x, y, _teffdiff(x, y),
                    levels=[1e-6, 1e-3, 1e-1, 1],
                    colors='k', linewidths=0.2)
    cs.clabel(fmt=u'$\Delta T_{eff} = %g °C$',
              manual=[(-10,2), (-18,5.5), (-14,7), (-5,8)])


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


def scatter(ltm, std, var, dat, reg, mon, zoom=False, large=False):
    """Draw scatter plots"""

    # initialize figure
    if large:
        fig = plt.figure(figsize=(178*mm, 135*mm))
        ax = fig.add_axes([9/178., 8/135., 167/178., 125/135.])
    else:
        fig = plt.figure(figsize=(85*mm, 65*mm))
        ax = fig.add_axes([9/85., 8/65., 74/85., 55/65.])

    # plot stdev data
    x = _extract(ltm, mon).data
    y = _extract(std, mon).data

    # set color table and color map
    clist = ['b', 'b', 'g', 'g', 'g', 'r', 'r', 'r', 'y', 'y', 'y', 'b']
    if reg == 'both':
        lon = ltm.coord('longitude').points
        lat = ltm.coord('latitude').points
        lon, lat = np.meshgrid(lon, lat)
        c = (lat > 0)
        cmap = ListedColormap(['gray', 'red'])
    elif mon == 'all':
        c = np.array([np.ones((x[0].shape))+i for i in range(12)])
        cmap = ListedColormap(clist)
    else:
        c = clist[mon]
        cmap = None
    if var == 'dteff': y = _teffdiff(x, y)
    ax.scatter(x, y, marker='+', c=c,  alpha=0.05, cmap=cmap)

    # set axes properties and labels
    _setxylim(reg, zoom=zoom)
    ax.set_xlabel(u'Long-term monthly mean (°C)')
    if var == 'sigma':
        ax.set_ylabel('Long-term monthly standard deviation (K)')
    if var == 'dteff':
        ax.set_yscale('log')
        ax.set_ylim(1e-6, 1e0)
        ax.set_ylabel('Effective temperature increase (K)')

    # add linear fit
    if mon == 'all':
        _linfit(x.compressed(), y.compressed())
        ax = fig.add_axes([10/178., 15/135., 80/178., 40/135.],
                          projection='3d')

    # add effective temperature contours and 3D plot
    if large and var == 'sigma':
        _dteffcontour()
        _dteff3d()

    # save
    if type(mon) is int: mon = str(mon+1).zfill(2)
    _savefig('stdev-param-scatter-%s-%s-%s-%s'
             % (var, dat, reg + zoom*'-zoom', mon + large*'-large'))


### Command-line interface ###

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--annvar', action='store_true',
                        help='Do not remove annual variability')
    parser.add_argument('-l', '--large', action='store_true',
                        help='Produce large figures')
    parser.add_argument('-z', '--zoom', action='store_true',
                        help='Zoom on summer values')
    parser.add_argument('-d', '--dataset', default='era40')
    parser.add_argument('-r', '--region', default='grl')
    parser.add_argument('-v', '--variable', default='sigma')
    parser.add_argument('--fig1', action='store_true', help='Draw Fig. 1')
    parser.add_argument('--fig2', action='store_true', help='Draw Fig. 2')
    parser.add_argument('--map', action='store_true', help=drawmap.__doc__)
    parser.add_argument('--scatter', action='store_true', help=scatter.__doc__)
    args = parser.parse_args()
    ann = args.annvar
    dat = args.dataset
    reg = args.region
    var = args.variable

    if args.fig1:
        plt.clf()
        ltm, std = _load('era40', 'both', ann=False)
        scatter(ltm, std, 'sigma', 'era40', 'both', 6, zoom=True)
    if args.fig2:
        plt.clf()
        ltm, std = _load('era40', 'grl', ann=False)
        scatter(ltm, std, 'sigma', 'era40', 'grl', 'all', zoom=False, large=True)
    ltm, std = _load(dat, reg, ann)
    dat = dat + ann*'ann'
    if args.scatter:
        for mon in range(12)+['all']:
            plt.clf()
            scatter(ltm, std, var, dat, reg, mon, zoom=args.zoom)
    if args.map:
        for mon in range(12):
            plt.clf()
            drawmap(ltm, std, dat, reg, mon)

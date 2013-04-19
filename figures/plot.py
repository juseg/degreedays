#!/usr/bin/env python

import cartopy.crs as ccrs
import iris
import iris.plot as iplt
from matplotlib import colors as mcolors
from matplotlib import ticker as mticker
from matplotlib import pyplot as plt

plt.rc('font', size=6)
plt.rc('savefig', dpi=254)
plt.rc('path', simplify=True)
mm = 1/25.4
pad = 2*mm
cbh = 4*mm
bot = 8*mm

fmt = 'png'

def stdev():

    # prepare figure
    mapw, maph = 80*mm, 40*mm
    figw =   mapw + 2*pad
    figh = 2*maph + 3*pad + cbh + bot
    fig = plt.figure(figsize=(figw, figh))

    # plot data
    filename = 'atm.nc'
    cube = iris.load(filename)[0]
    for i in (0, 1):
      ax = plt.axes(
        [pad/figw, ((1-i)*maph+(2-i)*pad+cbh+bot)/figh, mapw/figw, maph/figh],
        projection=ccrs.PlateCarree())
      ax.coastlines()
      cs = iplt.contourf(cube[i*6], 10, cmap = plt.cm.YlGnBu)
      iplt.contour(cube[i*6], 10, colors='k', linewidths=0.2)

    # add colorbar and save
    cax = plt.axes([pad/figw, bot/figh, 1-2*pad/figw, cbh/figh])
    cb = plt.colorbar(cs, cax, orientation='horizontal', format='%g')
    cb.set_label('Standard deviation of surface air temperature (K)')
    fig.savefig('stdev' + fmt)

def diff(isrelative=False):

    # prepare figure grid
    nproj = ccrs.NorthPolarStereo()
    sproj = ccrs.SouthPolarStereo()
    mapw, maph = 40*mm, 40*mm
    figw = 2*mapw + 3*pad
    figh = 2*maph + 3*pad + cbh + bot
    fig = plt.figure(figsize=(figw, figh))
    axx1 = (       pad)/figw
    axx2 = (mapw+2*pad)/figw
    axy1 = (maph+2*pad+cbh+bot)/figh
    axy2 = (     1*pad+cbh+bot)/figh
    axw = mapw/figw
    axh = maph/figh
    grid = [
      plt.axes([axx1, axy1, axw, axh], projection=nproj),
      plt.axes([axx2, axy1, axw, axh], projection=nproj),
      plt.axes([axx1, axy2, axw, axh], projection=nproj),
      plt.axes([axx2, axy2, axw, axh], projection=nproj)]
    cax = plt.axes([pad/figw, bot/figh, 1-2*pad/figw, cbh/figh])

    # plot data
    basename = ('r' if isrelative else 'a') + 'diff'
    filename = basename + '-%s.nc'
    data = [iris.load(filename % s)[1] for s in ['s0', 's5', 'avg', 'jja']]
    cases = ['0', '5', 'ANN', 'JJA']
    if isrelative:
      levs = [0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 100]
      cmap = plt.cm.YlGnBu
      cmap.set_under('w')
      cmap.set_over('k')
      norm = mcolors.BoundaryNorm(levs, 256, clip=True)
    else:
      levs = [i*50 for i in range(-6,7)]
      cmap = plt.cm.RdBu_r
      norm = mcolors.BoundaryNorm(levs, 256, clip=True)
    for i, ax in enumerate(grid):
      ax.set_xlim((-5e6, 5e6))
      ax.set_ylim((-5e6, 5e6))
      plt.sca(ax)
      cs = iplt.contourf(data[i], levs, cmap=cmap, norm=norm, extend='both')
      iplt.contour(data[i], levs, colors='k', linewidths=0.2, linestyles='solid')
      iplt.citation('$%s_\mathrm{%s}$' % ('r' if isrelative else 'd', cases[i]))
      ax.coastlines()

    # add colorbar and save
    if isrelative:
      topc = lambda x, pos: '%g%%' % (x*100) if abs(x) < 1 else '%g' % x
      cb = plt.colorbar(cs, cax, orientation='horizontal',
        format=mticker.FuncFormatter(topc))
      cb.set_label('Relative PDD error')
    else:
      cb = plt.colorbar(cs, cax, orientation='horizontal', format='%g')
      cb.set_label('Absolute PDD error (K day)')
    fig.savefig(basename + '.' + fmt)

if __name__ == '__main__':

    #stdev()
    diff(isrelative=False)
    diff(isrelative=True)


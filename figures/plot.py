#!/usr/bin/env python

import cartopy.crs as ccrs
import matplotlib as mpl
from matplotlib import pyplot as plt

import iris
import iris.plot as iplt

plt.rc('font', size=6)
plt.rc('savefig', dpi=254)
plt.rc('path', simplify=True)
mm = 1/25.4
pad = 2*mm
cbh = 4*mm
bot = 4*mm

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
        [pad/figw, (i*maph+(i+1)*pad+cbh+bot)/figh, mapw/figw, maph/figh],
        projection=ccrs.PlateCarree())
      ax.coastlines()
      cs = iplt.contourf(cube[i*6], 10,
        cmap = plt.cm.Greys)

    # add colorbar and save
    cax = plt.axes([pad/figw, bot/figh, 1-2*pad/figw, cbh/figh])
    cb = plt.colorbar(cs, cax, orientation='horizontal', format='%g')
    fig.savefig('stdev.png')

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
    ax1 = plt.axes([axx1, axy1, axw, axh], projection=nproj)
    ax2 = plt.axes([axx2, axy1, axw, axh], projection=sproj)
    ax3 = plt.axes([axx1, axy2, axw, axh], projection=nproj)
    ax4 = plt.axes([axx2, axy2, axw, axh], projection=sproj)
    cax = plt.axes([pad/figw, bot/figh, 1-2*pad/figw, cbh/figh])

    # plot data
    basename = ('r' if isrelative else 'a') + 'diff'
    filename = basename + '-s%s.nc'
    diff0 = iris.load_cube(filename % 0)
    diff5 = iris.load_cube(filename % 5)
    if isrelative:
      levs = [0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30, 100]
      cmap = plt.cm.RdPu
      norm = mpl.colors.BoundaryNorm(levs, 256, clip=True)
    else:
      levs = [i/2. - 2 for i in range(9)]
      cmap = plt.cm.RdBu
      norm = mpl.colors.BoundaryNorm(levs, 256, clip=True)
    for ax in ax1, ax2, ax3, ax4:
      ax.set_xlim((-5e6, 5e6))
      ax.set_ylim((-5e6, 5e6))
      ax.coastlines()
    for ax in ax1, ax2:
      plt.sca(ax)
      cs = iplt.contourf(diff0, levs, cmap=cmap, norm=norm)
    for ax in ax3, ax4:
      plt.sca(ax)
      cs = iplt.contourf(diff5, levs, cmap=cmap, norm=norm)

    # add colorbar and save
    cb = plt.colorbar(cs, cax, orientation='horizontal', format='%g')
    fig.savefig(basename + '.png')

if __name__ == '__main__':

    stdev()
    diff(isrelative=False)
    diff(isrelative=True)


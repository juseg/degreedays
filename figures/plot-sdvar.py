#!/usr/bin/env python
# coding: utf-8

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import iris
import iris.plot as iplt
from matplotlib import colors as mcolors
from matplotlib import ticker as mticker
from matplotlib import pyplot as plt

plt.rc('font', size=6)
plt.rc('savefig', dpi=254)
plt.rc('path', simplify=True)
plt.rc('mathtext', default='regular')
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
    filename = '../data/atm.nc'
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

def diff(varname, region, isrelative=False):

    # prepare projection and bounds
    xlim = (-5e6, 5e6)
    ylim = (-5e6, 5e6)
    if region == 'global':
      proj = ccrs.PlateCarree()
    if region == 'arctic':
      proj = ccrs.NorthPolarStereo()
    if region == 'antarctic':
      proj = ccrs.SouthPolarStereo()
    if region == 'greenland':
      proj = ccrs.NorthPolarStereo()
      xlim = (-3e6, 0)
      ylim = (-3e6, 0)

    # prepare figure grid
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
      plt.axes([axx1, axy1, axw, axh], projection=proj),
      plt.axes([axx2, axy1, axw, axh], projection=proj),
      plt.axes([axx1, axy2, axw, axh], projection=proj),
      plt.axes([axx2, axy2, axw, axh], projection=proj)]
    cax = plt.axes([pad/figw, bot/figh, 1-2*pad/figw, cbh/figh])

    # load data
    basename = ('r' if isrelative else 'a') + 'diff'
    filename = '../data/' + basename + '-%s.nc'
    cubenum = (1 if varname == 'smb' else 0)
    data = [iris.load(filename % s)[cubenum] for s in ['s0', 's5', 'avg', 'jja']]

    # pick colormap
    if isrelative:
      levs = [-10, -3, -1, -0.3, -0.1, -0.03, 0, 0.03, 0.1, 0.3, 1, 3, 10]
      cmap = plt.cm.RdBu
      norm = mcolors.BoundaryNorm(levs, 256)
      format = '%g'
    elif varname == 'smb':
      levs = [-1, -0.3, -0.1, -0.03, -0.01, -0.003, 0, 0.003, 0.01, 0.03, 0.1, 0.3, 1]
      cmap = plt.cm.RdBu
      norm = mcolors.BoundaryNorm(levs, 256)
      format = mticker.FuncFormatter(lambda x, pos: '%g' % (x*1000))
    else:
      levs = [i*50 for i in range(-4,5)]
      cmap = plt.cm.RdBu_r
      norm = None
      format = '%g'

    # plot and add labels
    cases = ['0', '5', 'ANN', 'JJA']
    ocean = cfeature.NaturalEarthFeature('physical', 'ocean', '50m',
      edgecolor = 'black',
      facecolor = 'white')
    for i, ax in enumerate(grid):
      if region != 'global':
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
      plt.sca(ax)
      cs = iplt.contourf(data[i], levs, cmap=cmap, norm=norm, extend='both', zorder=0)
      iplt.contour(data[i], levs, colors='k', linewidths=0.2, linestyles='solid', zorder=1)
      iplt.citation('$%s\mathrm{%s}_\mathrm{%s}$'
        % ('\delta' if isrelative else '\Delta', varname.upper(), cases[i]))
      if region=='greenland':
        ax.add_feature(ocean, zorder=2)
      else:
        ax.coastlines()

    # add colorbar
    cb = plt.colorbar(cs, cax, orientation='horizontal', format=format)
    if varname == 'smb':
      longvarname = 'Surface mass balance'
      unit = 'mm w.e. a$^{-1}$'
    else:
      longvarname = 'Positive degree day'
      unit = u'°C d'
    if isrelative:
      cb.set_label('%s relative error' % longvarname)
    else:
      cb.set_label('%s error (%s)' % (longvarname, unit))

    # save
    output = '%s-%s-%s.%s' % (varname, basename, region, fmt)
    print 'saving %s' % output
    fig.savefig(output)

if __name__ == '__main__':

    #stdev()
    for varname in ['pdd', 'smb']:
      for region in ['global', 'arctic', 'antarctic', 'greenland']:
        diff(varname, region, False)
        diff(varname, region, True)
    #diff('pdd', 'arctic')
    #diff('smb', 'greenland')

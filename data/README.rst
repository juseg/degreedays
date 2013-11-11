Data description
================

All files are in `NetCDF`_ format, see compatible `software`_. For methods and figures please refer to the paper [1]_.


Standard deviation of temperature
---------------------------------

This file contains values of long-term monthly standard deviation of daily mean surface air temperature from long-term monthly mean (Figure 1), as computed from `ERA-Interim`_ [2]_ data using `CDO`_:

* monthly standard deviations, `<std.nc>`_.


Positive degree days and surface mass balance
---------------------------------------------

These files contain distributions of positive degree days (Figure 2) and surface mass balance (Figure 3), computed by a `Python`_ code (`PyPDD`_):

* using monthly mean standard deviation, `<smb.nc>`_;
* using no temperature variability, `<smb-s0.nc>`_;
* using a constant 5 K standard deviation, `<smb-s5.nc>`_;
* using an annual mean of standard deviation, `<smb-avg.nc>`_;
* using a boreal summer (JJA) mean of standard deviation, `<smb-jja.nc>`_.


References
----------

.. [1] Seguinot, J., Spatial and seasonal effects of temperature variability in a positive degree day glacier surface mass balance model, Journal of Glaciology, 2013.
.. [2] Dee, D. P., S. M. Uppala, A. J. Simmons, P. Berrisford, P. Poli, S. Kobayashi, U. Andrae, M. A. Balmaseda, G. Balsamo, P. Bauer, P. Bechtold, A. C. M. Beljaars, L. van de Berg, J. Bidlot, N. Bormann, C. Delsol, R. Dragani, M. Fuentes, A. J. Geer, L. Haimberger, S. B. Healy, H. Hersbach, E. V. Hólm, L. Isaksen, P. K Ållberg, M. K Öhler, M. Matricardi, A. P. McNally, B. M. Monge-Sanz, J.-J. Morcrette, B.-K. Park, C. Peubey, P. de Rosnay, C. Tavolato, J.-N. Thépaut and F. Vitart, 2011. The ERA-Interim reanalysis configuration and performance of the data assimilation system, Quarterly Journal of the Royal Meteorological Society, 137(656), 553–597.

.. Links:

.. _CDO: http://code.zmaw.de/projects/cdo
.. _NetCDF: http://www.unidata.ucar.edu/software/netcdf/
.. _software: http://www.unidata.ucar.edu/software/netcdf/software.html
.. _ERA-Interim: http://apps.ecmwf.int/datasets/
.. _Python: http://python.org/
.. _PyPDD: http://github.com/jsegu/pypdd

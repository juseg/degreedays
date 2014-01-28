#!/bin/bash -e

# retrieve data from scooter
for dset in era40 erai ; do
    case $dset in
      era40 ) pp=5801 ;;
      erai  ) pp=7912 ;;
    esac
    for var in lsm tvl z sat.mon.$pp.avg sat.day.$pp{,.dev}.monstd ; do
        f=$dset.$var.nc
        [ -f $f ] || scp scooter:data/$dset/$f $f
    done
done

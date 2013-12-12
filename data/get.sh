#!/bin/bash -e

# retrieve data from scooter
for dset in era40 ; do
    for f in mask geop sat.mon.5801.avg \
             sat.day.5801.monstd sat.day.5801.dev.monstd ; do
        [ -f $dset.$f.nc ] || scp scooter:data/$dset/$f.nc $dset.$f.nc
    done
done

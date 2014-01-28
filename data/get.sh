#!/bin/bash -e

# retrieve data from scooter
for dset in era40 ; do
    for var in lsm tvl z sat.mon.5801.avg \
             sat.day.5801.monstd sat.day.5801.dev.monstd ; do
        f=$dset.$var.nc
        [ -f $f ] || scp scooter:data/$dset/$f $f
    done
done

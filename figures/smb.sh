#!/bin/bash -e

# create atmosphere file
data_path=$HOME/work/data/era-interim-longterm
cdo -O -b 64 merge\
  -chvar,v2t,air_temp $data_path/sat.7912.ltm.nc\
  -chvar,tp,precipitation -mulc,12 $data_path/tp.7912.ltm.nc\
  -chvar,v2t,air_temp_stdev $data_path/sat.7912.std.nc\
  atm.nc

# run pdd model
pypdd_path=$HOME/work/code/python/pypdd
$pypdd_path/pypdd.py -i atm.nc -o smb.nc
$pypdd_path/pypdd.py -i atm.nc -o smb-s0.nc --pdd-std-dev 0
$pypdd_path/pypdd.py -i atm.nc -o smb-s5.nc --pdd-std-dev 5

# compute differences
for s in 0 5; do
  cdo -O sub smb-s$s.nc smb.nc adiff-s$s.nc
  cdo -O abs -divc,2 -div adiff-s$s.nc -add smb.nc smb-s$s.nc rdiff-s$s.nc
done


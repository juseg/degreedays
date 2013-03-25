#!/bin/bash -e

data_path=$HOME/work/data/era-interim-longterm

# prepare standard deviation files
cdo chvar,v2t,air_temp_stdev $data_path/sat.7912.std.nc std.nc
cdo timavg std.nc std.avg.nc
cdo cat $(printf 'std.avg.nc %.s' {1..12}) std-avg.nc
cdo timavg -seltimestep,6,7,8 std.nc std.jja.nc
cdo cat $(printf 'std.jja.nc %.s' {1..12}) std-jja.nc
rm std.avg.nc std.jja.nc

# create atmosphere files
for f in std*.nc; do
  cdo -O -b 64 merge\
    -chvar,v2t,air_temp $data_path/sat.7912.ltm.nc\
    -chvar,tp,precipitation -mulc,12 $data_path/tp.7912.ltm.nc\
    -chvar,v2t,air_temp_stdev $f ${f/std/atm}
done

# run pdd model
pypdd_path=$HOME/work/code/python/pypdd
pypdd_args="-b --pdd-refreeze 0"
$pypdd_path/pypdd.py $pypdd_args -i atm.nc -o smb.nc
$pypdd_path/pypdd.py $pypdd_args -i atm.nc -o smb-s0.nc --pdd-std-dev 0
$pypdd_path/pypdd.py $pypdd_args -i atm.nc -o smb-s5.nc --pdd-std-dev 5
$pypdd_path/pypdd.py $pypdd_args -i atm-avg.nc -o smb-avg.nc
$pypdd_path/pypdd.py $pypdd_args -i atm-jja.nc -o smb-jja.nc

# compute differences
for f in smb-*.nc; do
  cdo -O sub $f smb.nc ${f/smb/adiff}
  cdo -O abs -div ${f/smb/adiff} smb.nc ${f/smb/rdiff}
done


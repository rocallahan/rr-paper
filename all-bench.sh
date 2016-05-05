#!/usr/bin/bash

export MEASURE=$HOME/rampage/target/release/rampage
export DO_RR_CONFIGS=0
export DO_DYNAMORIO=0

rm -rf traces/*

bash rr-bench-make.sh >& mem-make
bash rr-bench-cp.sh >& mem-cp
bash rr-bench-htmltest.sh >& mem-htmltest
bash rr-bench-octane.sh >& mem-octane
bash rr-bench-sambatest.sh >& mem-sambatest

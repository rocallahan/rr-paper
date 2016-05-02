#!/usr/bin/bash

MEASURE=time
# MEASURE=$HOME/rampage/target/release/rampage

rm -rf traces/*

bash rr-bench-make.sh >& output-make
bash rr-bench-cp.sh >& output-cp
bash rr-bench-htmltest.sh >& output-htmltest
bash rr-bench-octane.sh >& output-octane
bash rr-bench-sambatest.sh >& output-sambatest


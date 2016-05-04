#!/usr/bin/bash

export MEASURE="time -p"

rm -rf traces/*

bash rr-bench-cp.sh >& output-cp
bash rr-bench-make.sh >& output-make
bash rr-bench-htmltest.sh >& output-htmltest
bash rr-bench-octane.sh >& output-octane
bash rr-bench-sambatest.sh >& output-sambatest

export MEASURE=$HOME/rampage/target/release/rampage

rm -rf traces/*

bash rr-bench-make.sh >& mem-make
bash rr-bench-cp.sh >& mem-cp
bash rr-bench-htmltest.sh >& mem-htmltest
bash rr-bench-octane.sh >& mem-octane
bash rr-bench-sambatest.sh >& mem-sambatest

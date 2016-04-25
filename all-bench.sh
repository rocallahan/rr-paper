#!/usr/bin/bash

bash rr-bench-htmltest.sh >& ~/tmp/output-htmltest
bash rr-bench-make.sh >& ~/tmp/output-make
bash rr-bench-cp.sh >& ~/tmp/output-cp
bash rr-bench-octane.sh >& ~/tmp/output-octane
bash rr-bench-sambatest.sh >& ~/tmp/output-sambatest


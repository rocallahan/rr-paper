#!/usr/bin/bash

cd $HOME/mozilla-central
export MOZCONFIG=$HOME/.mozconfig-ff-opt

CLEANUP=""
CMD="./mach mochitest -f plain dom/html/test/forms"
CMD_SINGLE=$CMD
RR_NO_SYSCALLBUF_CMD="./mach mochitest -f plain --debugger $HOME/rr-paper/rr-no-syscallbuf.sh dom/html/test/forms"
RR_NO_CLONING_CMD="./mach mochitest -f plain --debugger $HOME/rr-paper/rr-no-clone.sh dom/html/test/forms"
RR_CMD="./mach mochitest -f plain --debugger rr dom/html/test/forms"
DR_CMD="./mach mochitest -f plain --debugger $HOME/dynamorio/obj/bin64/drrun dom/html/test/forms"
NAME=htmltest

source $HOME/rr-paper/rr-bench.sh

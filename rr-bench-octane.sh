#!/usr/bin/bash

cd $HOME/mozilla-central/js/src/octane

CLEANUP=""
CMD="$HOME/mozilla-central/obj-ff-opt/js/src/js run.js"
CMD_SINGLE="$HOME/mozilla-central/obj-ff-opt/js/src/js --thread-count=0 run.js"
RR_NO_SYSCALLBUF_CMD="rr record -F -n $CMD_SINGLE"
RR_NO_CLONING_CMD="rr record -F --no-read-cloning $CMD_SINGLE"
RR_CMD="rr -F record $CMD_SINGLE"
DR_CMD="$HOME/dynamorio/obj/bin64/drrun $CMD"

source $HOME/rr-paper/rr-bench.sh

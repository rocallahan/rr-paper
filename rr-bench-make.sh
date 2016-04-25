#!/usr/bin/bash

export CCACHE_DISABLE=1

CLEANUP="make -C $HOME/dynamorio2/obj clean"
CMD="make -C $HOME/dynamorio2/obj -j8"
CMD_SINGLE="make -C $HOME/dynamorio2/obj -j1"
RR_NO_SYSCALLBUF_CMD="rr record -F -n $CMD_SINGLE"
RR_NO_CLONING_CMD="rr record -F --no-read-cloning $CMD_SINGLE"
RR_CMD="rr -F record $CMD_SINGLE"
DR_CMD="$HOME/dynamorio/obj/bin64/drrun $CMD"

source $HOME/rr-paper/rr-bench.sh

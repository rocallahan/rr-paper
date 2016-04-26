#!/usr/bin/bash

CLEANUP="rm -rf $HOME/glibc2"
CMD="cp -a $HOME/glibc $HOME/glibc2"
CMD_SINGLE=$CMD
RR_NO_SYSCALLBUF_CMD="rr record -n $CMD_SINGLE"
RR_NO_CLONING_CMD="rr record --no-read-cloning $CMD_SINGLE"
RR_CMD="rr record $CMD_SINGLE"
DR_CMD="$HOME/dynamorio/obj/bin64/drrun $CMD"
NAME=cp

source $HOME/rr-paper/rr-bench.sh

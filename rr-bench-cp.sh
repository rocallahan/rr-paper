#!/usr/bin/bash

CLEANUP="rm -rf $HOME/glibc2"
CMD="cp -a $HOME/glibc $HOME/glibc2"
RR_NO_SYSCALLBUF_CMD="rr record -n $CMD"
RR_NO_CLONING_CMD="rr record --no-read-cloning $CMD"
RR_CMD="rr record $CMD"
DR_CMD="$HOME/dynamorio/obj/bin64/drrun $CMD"

source ./rr-bench.sh

#!/usr/bin/bash

cd $HOME/samba

CLEANUP=""
CMD="make test TESTS=samba4.echo.udp"
CMD_SINGLE=$CMD
RR_NO_SYSCALLBUF_CMD="rr record -F -n $CMD_SINGLE"
RR_NO_CLONING_CMD="rr record -F --no-read-cloning $CMD_SINGLE"
RR_CMD="rr -F record $CMD_SINGLE"
DR_CMD="$HOME/dynamorio/obj/bin64/drrun $CMD"

source $HOME/rr-paper/rr-bench.sh

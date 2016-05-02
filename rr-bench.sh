N=6

ulimit -n 4096

echo ^^^^ NORMAL

for i in $(seq 1 $N); do
  $CLEANUP
  $MEASURE $CMD
done

echo ^^^^ SINGLE-CORE

for i in $(seq 1 $N); do
  $CLEANUP
  $MEASURE taskset 4 $CMD_SINGLE
done

rm -rf $HOME/.local/share/rr
echo ^^^^ RECORD-NO-SYSCALLBUF

traces=(dummy)
for i in $(seq 1 $N); do
  $CLEANUP
  $MEASURE $RR_NO_SYSCALLBUF_CMD
  traces+=(`realpath ~/.local/share/rr/latest-trace`)
done

echo ^^^^ REPLAY-NO-SYSCALLBUF

for i in $(seq 1 $N); do
  $MEASURE rr replay -F -a ${traces[i]}
done

rm -rf $HOME/.local/share/rr
echo ^^^^ RECORD-NO-CLONING

for i in $(seq 1 $N); do
  $CLEANUP
  $MEASURE $RR_NO_CLONING_CMD
done

rm -rf $HOME/.local/share/rr
echo ^^^^ RECORD

traces=(dummy)
for i in $(seq 1 $N); do
  $CLEANUP
  $MEASURE $RR_CMD
  traces+=(`realpath ~/.local/share/rr/latest-trace`)
done

echo ^^^^ REPLAY

for i in $(seq 1 $N); do
  $MEASURE rr replay -F -a ${traces[i]}
  mv ${traces[i]} $HOME/rr-paper/traces/$NAME-$i
done

echo ^^^^ DYNAMORIO

for i in $(seq 1 $N); do
  $CLEANUP
  $MEASURE $DR_CMD
done


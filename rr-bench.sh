N=2

ulimit -n 4096

echo ^^^^ NORMAL

for i in $(seq 1 $N); do
  $CLEANUP
  time $CMD
done

echo ^^^^ SINGLE-CORE

for i in $(seq 1 $N); do
  $CLEANUP
  time taskset 4 $CMD_SINGLE
done

rm -rf $HOME/.local/share/rr
echo ^^^^ RECORD-NO-SYSCALLBUF

traces=(dummy)
for i in $(seq 1 $N); do
  $CLEANUP
  time $RR_NO_SYSCALLBUF_CMD
  traces+=(`realpath ~/.local/share/rr/latest-trace`)
done

echo ^^^^ REPLAY-NO-SYSCALLBUF

for i in $(seq 1 $N); do
  time rr replay -F -a ${traces[i]}
done

rm -rf $HOME/.local/share/rr
echo ^^^^ RECORD-NO-CLONING

for i in $(seq 1 $N); do
  $CLEANUP
  time $RR_NO_CLONING_CMD
done

rm -rf $HOME/.local/share/rr
echo ^^^^ RECORD

traces=(dummy)
for i in $(seq 1 $N); do
  $CLEANUP
  time $RR_CMD
  traces+=(`realpath ~/.local/share/rr/latest-trace`)
done

echo ^^^^ REPLAY

for i in $(seq 1 $N); do
  time rr replay -F -a ${traces[i]}
done

echo ^^^^ DYNAMORIO

for i in $(seq 1 $N); do
  $CLEANUP
  time $DR_CMD
done


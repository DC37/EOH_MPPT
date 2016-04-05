#!/bin/sh
# Kills Python.
# Remember to "allow executing file as program" if moving this file from a
# removable medium (Right-click -> Properties -> Permissions).

signal=TERM

# Get PID's of processes to kill, then kill them with specified signal
pgrep '^python$' | while read pid
do
   kill -$signal $pid
done

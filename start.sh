#!/bin/bash

./server/bin/server &
python3 client &

wait -n
exit $?
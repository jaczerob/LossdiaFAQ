#!/bin/bash

./server &
python3 client &

wait -n
exit $?
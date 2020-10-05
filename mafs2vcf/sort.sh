#!/bin/sh

(tail -n +2 $1 | awk '!seen[$0]++' | sort -k1 -k2 > $2) || echo "Error sorting"

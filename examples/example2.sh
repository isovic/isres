#! /bin/sh

loc=`dirname $0`

# Calls a parallel-ismemtest.sh script that runs ismemtest in parallel. There are 4 processes, each allocating 102 MB of memory, and running for 3000 ms.
$loc/../isres.py $loc/examples-output/example2 k $loc/../ismemtest/parallel-ismemtest.sh

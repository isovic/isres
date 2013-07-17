#! /bin/sh

loc=`dirname $0`

# Allocate 1234 MB of memory, and waste 3000 ms of your time.
$loc/../isres.py $loc/examples-output/example1 B $loc/../ismemtest/ismemtest 1024 3000

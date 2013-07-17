#! /bin/bash

loc=`dirname $0`

$loc/ismemtest 102 3000 & $loc/ismemtest 102 3000 & $loc/ismemtest 102 3000 & $loc/ismemtest 102 3000

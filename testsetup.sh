#!/bin/bash
## begin license ##
#
# All rights reserved.
#
# Copyright (C) 2012-2015 Seecr (Seek You Too B.V.) http://seecr.nl
#
## end license ##

set -o errexit
source /usr/share/seecr-tools/functions.d/test
mydir=$(cd $(dirname $0); pwd)

definePythonVars $(pyversions -vd)
rm -rf tmp build
${PYTHON} setup.py install --root tmp

cp -r test tmp/test

removeDoNotDistribute tmp
#find tmp -type f -exec sed -e "
#    s,^usrSharePath.*$,usrSharePath='$mydir/tmp/usr/share/gustos-server'," -i {} \;

runtests "$@"

rm -rf tmp build

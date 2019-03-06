## begin license ##
#
# All rights reserved.
#
# Copyright (C) 2013-2014 Seecr (Seek You Too B.V.) http://seecr.nl
#
## end license ##

from gustos.client import CpuUsageLxc

def meter():
    return dict(meter=CpuUsageLxc(), interval=60)


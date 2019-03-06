## begin license ##
#
# All rights reserved.
#
# Copyright (C) 2013-2014 Seecr (Seek You Too B.V.) http://seecr.nl
#
## end license ##

from gustos.client.cpuusage import CpuUsage

def meter():
    return dict(meter=CpuUsage(), interval=60)


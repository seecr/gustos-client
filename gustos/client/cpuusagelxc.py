## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2012-2014, 2018 Seecr (Seek You Too B.V.) https://seecr.nl
#
# This file is part of "Gustos-Client"
#
# "Gustos-Client" is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# "Gustos-Client" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Gustos-Client"; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
## end license ##

from gustos.common.units import PERCENTAGE
from socket import gethostname
from os.path import join
from time import sleep

class CpuUsageLxc(object):
    def __init__(self, group='CPU usage', chartLabel='CPU', root="/", hostname=None):
        self._group = group
        self._chartLabel = chartLabel
        realHostName = gethostname().split('.')[0] if hostname is None else hostname
        self._path = join(root, "sys", "fs", "cgroup", "cpuacct", "lxc", realHostName)

    def values(self):
        return {
            self._group: {
                self._chartLabel: {
                    "usage": { PERCENTAGE: self.cpuUsage() }
                }
            }
        }
    
    def cpuAcctUsage(self):
        with open(join(self._path, "cpuacct.usage")) as fp:
            return int(fp.read())

    def cpuUsage(self, measureTime=1):
        t0 = self.cpuAcctUsage()
        sleep(measureTime)
        delta = self.cpuAcctUsage() - t0

        return int(delta / 10**7)

    def __repr__(self):
        return 'CpuUsageLxc()'

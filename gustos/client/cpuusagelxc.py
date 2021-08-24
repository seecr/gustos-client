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
from os.path import join, isfile, isdir
from os import listdir
from time import sleep

class CpuUsageLxc(object):
    def __init__(self, group='CPU usage', root="/"):
        self._group = group
        self._path = join(root, "sys", "fs", "cgroup", "cpu,cpuacct", "lxc")


    def values(self):
        return {
            self._group: {vm:dict(usage={PERCENTAGE: delta}) for vm,delta in self.cpuUsage().items()}
        }
    
    def cpuAcctUsage(self, vm):
        filename = join(self._path, vm, "cpuacct.usage")
        if not isfile(filename):
            return None

        with open(join(self._path, vm, "cpuacct.usage")) as fp:
            return int(fp.read())

    def cpuUsage(self):
        vms = [vm for vm in listdir(self._path) if isdir(join(self._path, vm))]
        t0 = {vm:self.cpuAcctUsage(vm) for vm in vms}
        self._sleep()
        t1 = {vm:self.cpuAcctUsage(vm) for vm in vms}

        return {vm:delta(t0[vm], t1[vm]) for vm in vms if not t0[vm] is None and not t1[vm] is None}

    def _sleep(self):
        sleep(1)

    def __repr__(self):
        return 'CpuUsageLxc()'

def delta(t0, t1):
    # t0-t1 is the number of nanoseconds the cgroup used the CPU during the self_measureTime
    # there are 1.000.000.000 (10^9) nanoseconds in a second
    #
    # return the percentage of 1 second used.
    return int((t1-t0) / 10**7)

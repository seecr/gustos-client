## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2014-2015, 2018, 2021 Seecr (Seek You Too B.V.) https://seecr.nl
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

from time import sleep
from gustos.common.units import PERCENTAGE, MEMORY
from subprocess import Popen, PIPE
from os import listdir

SERVICE_DIR = "/etc/service"

def _readStat(pid):
    fields = ("pid", "comm", "state", "ppid", "pgid", "sid", "tty_nr", "tty_pgrp", "flags", "min_flt", "cmin_flt", "maj_flt", "cmaj_flt", "utime", "stime", "cutime", "cstime", "priority", "nicev", "num_threads", "it_real_value", "vsize", "rss", "rsslim", "start_code", "end_code", "start_stack", "esp", "eip", "pending", "blocked", "sigign", "sigcatch", "wchan", "zero1", "zero2", "exit_signal", "cpu", "rt_priority", "policy")
    return dict(list(zip(fields, open('/proc/%s/stat' % pid).read().split())))

def _readStatus(pid):
    result = {}
    for line in open('/proc/%s/status' % pid):
        key, value = line.split('\t', 1)
        result[key[:-1]] = value.strip()
    return result

def measureCpu(pid):
    cpuData = _readStat(pid)
    utime_start = int(cpuData['utime'])
    cutime_start = int(cpuData['cutime'])
    stime_start = int(cpuData['stime'])
    cstime_start = int(cpuData['cstime'])
    sleep(1)
    cpuData = _readStat(pid)
    utime = (int(cpuData['utime']) - int(utime_start))/ 1.0
    cutime = (int(cpuData['cutime']) - int(cutime_start))/ 1.0
    stime = (int(cpuData['stime']) - int(stime_start))/ 1.0
    cstime = (int(cpuData['cstime']) - int(cstime_start))/ 1.0
    return utime + cutime, stime + cstime

def measureMemory(pid):
    procStatus = _readStatus(pid)
    return int(procStatus['VmRSS'].split()[0])*1024

class ServiceMonitor(object):
    def __init__(self, names=None, excludedNames=None, serviceDir=SERVICE_DIR):
        self._names = set() if names is None else set(names)
        self._excludedNames = set() if excludedNames is None else set(excludedNames)
        self._serviceDir = serviceDir

    def _findPid(self, name):
        ouput = Popen("svstat %s/%s" % (self._serviceDir, name), shell=True, stdout=PIPE, stderr=PIPE).communicate()[0]
        if ': up' in ouput:
            return ouput.split()[3][:-1]
        return None

    def _measure(self, pid):
        return sum(measureCpu(pid)), measureMemory(pid)

    def _serviceNames(self):
        if self._names:
            return sorted(self._names)
        return sorted(set(listdir(self._serviceDir)) - self._excludedNames)

    def values(self):
        results = []
        for name in self._serviceNames():
            pid = self._findPid(name)
            if pid is None:
                continue
            try:
                cpuUsage, memUsage = self._measure(pid)
            except IOError:
                continue
            result = {"CPU usage": {}, "Memory": {}}
            result["CPU usage"][name] = {'usage': {
                            PERCENTAGE: cpuUsage
                        }}
            result["Memory"][name] = {'usage': {
                            MEMORY: memUsage,
                        }}
            results.append(result)
        if results:
            return results

    def __repr__(self):
        if self._names:
            contents = "names=" + repr(sorted(self._names))
        else:
            contents = "excludedNames=" + repr(sorted(self._excludedNames))
        return "ServiceMonitor({})".format(contents)


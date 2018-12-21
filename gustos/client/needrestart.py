## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2012-2015, 2018 Seecr (Seek You Too B.V.) https://seecr.nl
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

from gustos.common.units import COUNT
from gustos.client import VERSION
from subprocess import Popen, PIPE

import psutil

class NeedRestart(object):
    def __init__(self, ignore=None):
        self._ignore = ignore if ignore else []

    def _processIter(self): 
        return psutil.process_iter()

    def _processInfo(self):
        p = Popen(["ps", "axho", "pid,cgroup"], stdout=PIPE, stderr=PIPE)
        try:
            out, err = p.communicate()
        finally:
            p.wait()
        return out

    def _hostOnlyProcesses(self, psOutput):
        processes = []
        for line in (line.strip() for line in psOutput.split("\n") if ' ' in line.strip()):
            pid, cgroup = line.split(" ", 1)
            if not '/lxc/' in cgroup:
                processes.append(int(pid))
        return processes

    def _isVMHost(self):
        p = Popen(["ps", "ho", "cgroup", "1"], stdout=PIPE, stderr=PIPE)
        try:
            out, err = p.communicate()
        finally:
            p.wait()
        return out.strip() == "-"

    def _memoryMaps(self, proc):
        return proc.memory_maps if hasattr(proc, "memory_maps") else proc.get_memory_maps

    def usingDeletedSOs(self):
        def _usingDeletedSO(p):
            memoryMaps = self._memoryMaps(p)
            
            try:
                for mm in memoryMaps():
                    if '(deleted)' in mm.path and ('.so.' in mm.path or '.so ' in mm.path):
                        return True
            except ValueError:
                pass
            except psutil.NoSuchProcess:
                pass

            return False
        foundProcesses = set(p for p in self._processIter() if _usingDeletedSO(p))
        if self._isVMHost():
            hostOnlyProcesses = self._hostOnlyProcesses(self._processInfo())
            foundProcesses = [process for process in foundProcesses if process.pid in hostOnlyProcesses]

        def getName(p):
            try:
                return p.name()
            except:
                return p.name
        return [p for p in foundProcesses if not getName(p) in self._ignore]

    def values(self):
        usingDeletedSOs = set(p.name() for p in self.usingDeletedSOs())

        return {'Need restart': {'Need restart': {'Processes': {'count': len(usingDeletedSOs)}}}}

    def __repr__(self):
        return 'NeedRestart()'


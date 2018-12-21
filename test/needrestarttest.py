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

from seecr.test import SeecrTestCase

from gustos.client import NeedRestart
from gustos.common.units import COUNT

from psutil import NoSuchProcess

def no_restarts_processIter():
    return [
        MockProcess(100, "proc-1", ['/some/file']), 
        MockProcess(200, "proc-2", ['/lib/lib-1.so', '/lib/lib-2.so.0'])]

def with_restarts_processIter():
    return [
        MockProcess(100, "proc-1", ['/some/file (deleted)']), 
        MockProcess(200, "proc-2", ['/lib/lib-1.so (deleted)', '/lib/lib-2.so.0']),
        MockProcess(300, "proc-3", ['/lib/lib-1.so', '/lib/lib-2.so.0 (deleted)'])]

def mock_ps_output_vm():
    return """ 100 9:perf_event:/lxc/avarus-dev,7:net_cls,net_prio:/lxc/avarus-dev,6:freezer:/lxc/avarus-dev,4:memory:/lxc/avarus-dev,2:cpuset:/lxc/
  200 9:perf_event:/lxc/avarus-dev,7:net_cls,net_prio:/lxc/avarus-dev,6:freezer:/lxc/avarus-dev,4:memory:/lxc/avarus-dev,2:cpuset:/lxc/
  300 9:perf_event:/lxc/avarus-dev,7:net_cls,net_prio:/lxc/avarus-dev,6:freezer:/lxc/avarus-dev,4:memory:/lxc/avarus-dev,2:cpuset:/lxc/
"""

def mock_ps_output_host():
    return """ 100 9:perf_event:/lxc/backup,7:net_cls,net_prio:/lxc/backup,6:freezer:/lxc/backup
  200 5:devices:/system.slice/seecr-daemontools-run.service,1:name=systemd:/system.slice/seecr-daemontools-run.service
  300 9:perf_event:/lxc/backup,7:net_cls,net_prio:/lxc/backup,6:freezer:/lxc/backup
  400 -
"""

class NeedRestartTest(SeecrTestCase):
    def testMeterNoRestarts(self):
        meter = NeedRestart()
        meter._processIter = no_restarts_processIter
        meter._processInfo = mock_ps_output_vm
        meter._isVMHost = lambda: False
        self.assertEqual({
            'Need restart': {
                'Need restart': {
                    'Processes': { COUNT: 0 }
                }
            }
        }, meter.values())

    def testMeterNoRestartsWithDEL(self):
        meter = NeedRestart()
        meter._processIter = with_restarts_processIter
        meter._processInfo = mock_ps_output_vm
        meter._isVMHost = lambda: False
        self.assertEqual({
            'Need restart': {
                'Need restart': {
                    'Processes': { COUNT: 2 }
                }
            }
        }, meter.values())

    def testFilterProcsForVMHost(self):
        meter = NeedRestart()
        meter._processIter = with_restarts_processIter
        meter._processInfo = mock_ps_output_host
        meter._isVMHost = lambda: True
        self.assertEqual({
            'Need restart': {
                'Need restart': {
                    'Processes': { COUNT: 1 }
                }
            }
        }, meter.values())

    def testMeterIgnoreSpecifiedProcesses(self):
        meter = NeedRestart(ignore=['proc-2'])
        meter._processIter = with_restarts_processIter
        meter._processInfo = mock_ps_output_vm
        meter._isVMHost = lambda: False
        self.assertEqual({
            'Need restart': {
                'Need restart': {
                    'Processes': { COUNT: 1 }
                }
            }
        }, meter.values())

    def testNoSuchProcessException(self):
        meter = NeedRestart()
        def raiseException():
            raise NoSuchProcess(42, "mock")
        meter._processIter = with_restarts_processIter
        meter._memoryMaps = lambda *args, **kwargs: raiseException
        meter._processInfo = mock_ps_output_vm
        meter._isVMHost = lambda: False
        self.assertEqual({
            'Need restart': {
                'Need restart': {
                    'Processes': { COUNT: 0 }
                }
            }
        }, meter.values())



class MockProcess(object):
    def __init__(self, pid, name, paths):
        self.pid = pid
        self._name = name
        self.paths = paths
    def name(self):
        return self._name
    def memory_maps(self):
        class MemoryMap(object):
            def __init__(this, path):
                this.path = path
        return [MemoryMap(path) for path in self.paths]

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
from seecr.test.utils import mkdir

from gustos.client import CpuUsageLxc
from gustos.common.units import PERCENTAGE
from os.path import join
from os import listdir
from shutil import rmtree

class CpuUsageLxcTest(SeecrTestCase):
    def testMeterAll(self):
        VMS = ['vm-1', 'vm-2', 'vm-3']
        meter = CpuUsageLxc(root=self.tempdir)
        meter._sleep = lambda: self._writeValues(VMS, values=["294471002154", "294773669923", "296689468871"])
        self._writeValues(VMS, values=["294371002154", "294715774832", "296185458359"])

        self.assertEqual({
            'CPU usage': {
                'vm-3': {
                    'usage': {
                        'percentage': 50
                    }
                },
                'vm-2': {
                    'usage': {
                        'percentage': 5
                    }
                },
                'vm-1': {
                    'usage': {
                        'percentage': 10
                    }
                }
            }
        }, meter.values())

    def testMeterAllMissingSecondTiming(self):
        meter = CpuUsageLxc(root=self.tempdir)
        meter._sleep = lambda: self._writeValues(['vm-1', 'vm-2'], cleanUp=['vm-3'], values=["294471002154", "294773669923"])
        self._writeValues(['vm-1', 'vm-2', 'vm-3'], values=["294371002154", "294715774832", "296185458359"])

        self.assertEqual({
            'CPU usage': {
                'vm-2': {
                    'usage': {
                        'percentage': 5
                    }
                },
                'vm-1': {
                    'usage': {
                        'percentage': 10
                    }
                }
            }
        }, meter.values())

    def testMeterAllMissingFirstTiming(self):
        meter = CpuUsageLxc(root=self.tempdir)
        meter._sleep = lambda: self._writeValues(
            ['vm-1', 'vm-2', 'vm-3'],
            values=["294471002154", "294773669923", "296689468871"])
        self._writeValues(['vm-1', 'vm-2'], values=["294371002154", "294715774832"])

        self.assertEqual({
            'CPU usage': {
                'vm-2': {
                    'usage': {
                        'percentage': 5
                    }
                },
                'vm-1': {
                    'usage': {
                        'percentage': 10
                    }
                }
            }
        }, meter.values())



    def _writeValues(self, vms, cleanUp=None, values=None):
        cleanUp = cleanUp or []
        baseDir = mkdir(self.tempdir, "sys", "fs", "cgroup", "cpu,cpuacct", "lxc")
        for each in listdir(baseDir):
            if each in cleanUp:
                rmtree(join(baseDir, each))
        for each in vms:
            vmDir = mkdir(baseDir, each)
            with open(join(vmDir, 'cpuacct.usage'), "w") as fp:
                fp.write(values.pop(0))

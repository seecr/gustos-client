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

class CpuUsageLxcTest(SeecrTestCase):
    def testMeter(self):
        VM_NAME = "mock_vm"
        cpuAcctDir = mkdir(self.tempdir, "sys", "fs", "cgroup", "cpuacct")
        meter = CpuUsageLxc(root=self.tempdir, hostname=VM_NAME)

        values = [
            "294371002154", "294715774832", "296185458359", "296639043978",
            "296660514083", "296673669923", "296689468871", "296703166248",
            "296726751877", "296739486976", "296753427937", "296764687332",
            "298103553675", "299159027203", "299175741441", "299189317118",
            "299204570690", "299217023071", "299229234789", "299248973243",
            "299262147098", "299273877350"
        ]

        originalCpuAcctUsage = meter.cpuAcctUsage
        def cpuAcctUsage():
            with open(join(cpuAcctDir, "cpuacct.usage"),"w") as fp:
                fp.write(values.pop(0))
            return originalCpuAcctUsage()
        meter.cpuAcctUsage = cpuAcctUsage

        percentages = []
        while len(values) > 0:
            percentages.append(meter.cpuUsage(measureTime=0.01))

        self.assertEqual([34, 45, 1, 1, 1, 1, 105, 1, 1, 1, 1], percentages)

        meter.cpuUsage = lambda: 45
        self.assertEqual({
                'CPU usage': {
                    'CPU' : {
                        'usage': { PERCENTAGE: 45 },
                    }
                }
            },
            meter.values())

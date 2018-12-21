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

from gustos.client import CpuUsage
from gustos.common.units import PERCENTAGE

class CpuUsageTest(SeecrTestCase):
    def testMeter(self):
        meter = CpuUsage(measuringTime=0)

        values = [
            'cpu  74905 0 10298 95205334 18793 1802 2274 0 0',
            'cpu  74905 0 11298 95206334 20793 1802 2274 0']

        meter._readProcState = lambda: values.pop(0)
        self.assertEqual((25.0, 50.0), meter.usage())

    def testAsJson(self):
        meter = CpuUsage(measuringTime=0)
        values = [
            'cpu  74905 0 10298 95205334 18793 1802 2274 0 0',
            'cpu  74905 0 11298 95206334 20793 1802 2274 0']
        meter._readProcState = lambda: values.pop(0)
        self.assertEqual({
                'CPU usage': {
                    'CPU': {
                        'usage': {
                            PERCENTAGE: 25.0
                        },
                        'iowait': {
                            PERCENTAGE: 50.0
                        }
                    }
                }
            }, meter.values())

## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2019 Seecr (Seek You Too B.V.) https://seecr.nl
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
from os.path import join

from gustos.client import Uptime

from gustos.common.units import COUNT

class UptimeTest(SeecrTestCase):
    def testMeter(self):
        with open(join(self.tempdir, "uptime"), "w") as f:
            f.write("164591.29 657603.91")

        meter = Uptime(_file=join(self.tempdir, "uptime"))

        self.assertEqual({
                'Uptime': {
                    'System': {
                        'days': { COUNT: 1 }
                    }
                }
            }, meter.values())
    
    def testErrorHandling(self):
        meter = Uptime(_file=join(self.tempdir, "uptime"))

        self.assertEqual({
                'Uptime': {
                    'System': {
                        'days': { COUNT: 0 }
                    }
                }
            }, meter.values())

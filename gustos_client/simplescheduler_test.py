## begin license ##
#
# "Gustos" is a monitoring tool by Seecr.
# This client side code for connecting with Gustos server.
#
# Copyright (C) 2014, 2018, 2026 Seecr (Seek You Too B.V.) https://seecr.nl
#
# This file is part of "Gustos-Client"
#
# "Gustos-Client" is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# "Gustos-Client" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Gustos-Client".  If not, see <http://www.gnu.org/licenses/>.
#
## end license ##

from seecr.test import SeecrTestCase
from gustos_client.simplescheduler import SimpleScheduler

class SimpleSchedulerTest(SeecrTestCase):

    def testEmpty(self):
        ss = SimpleScheduler()
        self.assertRaises(ValueError, lambda: ss.step())

    def testSchedule(self):
        ss = SimpleScheduler()
        calls = []
        def doTimer():
            calls.append(True)

        ss.addTimer(0.1, doTimer)
        ss.step()
        self.assertEqual([True], calls)
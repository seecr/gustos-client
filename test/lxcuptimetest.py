## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2024 Seecr (Seek You Too B.V.) https://seecr.nl
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

from gustos.client import LxcUptime
from gustos.common.units import COUNT

class LxcUptimeTest(SeecrTestCase):
    def test_meter(self):
        meter = LxcUptime(svstat_command=lambda: OUTPUT)
        self.assertEqual({
            "LXC": {
                "Uptimes": {
                    "stats-ms-dev": {COUNT: 490566},
                    "stretch-64": {COUNT: 490566},
                    "VHVMc": {COUNT: 489303},
                    "VHVM": {COUNT: 0},
                    "vpn-c": {COUNT: 490566},
                    "wiki": {COUNT: 0},
                    "workshop": {COUNT: 0},
                },
                'Downtimes': {'VHVM': {'count': 490573},
                    'VHVMc': {'count': 0},
                    'stats-ms-dev': {'count': 0},
                    'stretch-64': {'count': 0},
                    'vpn-c': {'count': 0},
                    'wiki': {'count': 490573},
                    'workshop': {'count': 490573}},
                "Status": {
                    "up": {COUNT: 4},
                    "down": {COUNT: 2},
                    "down-up": {COUNT: 1}
                }
            }},
            meter.values())




OUTPUT = """/etc/service/lxc-stats-ms-dev: up (pid 9106) 490566 seconds
/etc/service/lxc-stretch-64: up (pid 9096) 490566 seconds
/etc/service/lxc-VHVM: down 490573 seconds, normally up
/etc/service/lxc-VHVMc: up (pid 7709) 489303 seconds
/etc/service/lxc-vpn-c: up (pid 9114) 490566 seconds
/etc/service/lxc-wiki: down 490573 seconds
/etc/service/lxc-workshop: down 490573 seconds
"""

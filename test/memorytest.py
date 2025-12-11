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

from gustos.client import Memory
from gustos.common.units import MEMORY


class MemoryTest(SeecrTestCase):
    def testMeter(self):
        meter = Memory()
        meter._readProcMeminfo = lambda: {
            "MemFree": 142696,
            "MemTotal": 4035280,
            "Slab": 1234,
            "Buffers": 48444,
            "Cached": 275152,
        }

        self.assertEqual(
            {
                "Memory": {
                    "Main memory": {
                        "free": {MEMORY: 142696 * 1024},
                        "slab": {MEMORY: 1234 * 1024},
                        "buffers": {MEMORY: 48444 * 1024},
                        "cached": {MEMORY: 275152 * 1024},
                        "remaining": {
                            MEMORY: (4035280 - 142696 - 1234 - 48444 - 275152) * 1024
                        },
                        "available": {MEMORY: (142696 + 48444 + 275152) * 1024},
                    }
                }
            },
            meter.values(),
        )

    def testMeter(self):
        meter = Memory(disabled=("slab", "buffers", "cached", "remaining", "available"))
        meter._readProcMeminfo = lambda: {
            "MemFree": 142696,
            "MemTotal": 4035280,
            "Slab": 1234,
            "Buffers": 48444,
            "Cached": 275152,
        }

        self.assertEqual(
            {
                "Memory": {
                    "Main memory": {
                        "free": {MEMORY: 142696 * 1024},
                    }
                }
            },
            meter.values(),
        )

    def testOnlyMemTotalAndFree(self):
        meter = Memory()
        meter._readProcMeminfo = lambda: {"MemFree": 142696, "MemTotal": 4035280}

        self.assertEqual(
            {
                "Memory": {
                    "Main memory": {
                        "free": {MEMORY: 142696 * 1024},
                        "remaining": {MEMORY: (4035280 - 142696) * 1024},
                    }
                }
            },
            meter.values(),
        )

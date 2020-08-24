## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2012-2014, 2018, 2020 Seecr (Seek You Too B.V.) https://seecr.nl
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

from gustos.client import Diskspace

from gustos.common.units import MEMORY

class DiskspaceTest(SeecrTestCase):
    def testMeter(self):
        meter = Diskspace(path='/')
        meter._vfscall = lambda *args, **kwargs: (4096, 4096, 2968484, 197065, 197065, 0, 0, 0, 0, 255)

        self.assertEqual({
                'available': 807178240,
                'used': 12158910464-807178240,
            }, meter._diskUsage('/'))
        self.assertEqual({
                'Disk space': {
                    '/': {
                        'available': { MEMORY: 807178240 },
                        'used': { MEMORY: 11351732224 }
                    }
                }
            }, meter.values())

        meter._vfscall = lambda *args, **kwargs: (2048, 4096, 2968484, 197065, 197065, 0, 0, 0, 0, 255)
        self.assertEqual({
                'available': 807178240 / 2,
                'used': (12158910464-807178240) / 2,
            }, meter._diskUsage('/'))

    def testIncludeInodeIfAvail(self):
        meter = Diskspace(path='/')
        meter._vfscall = lambda *args, **kwargs: (4096, 4096, 2968484, 197065, 197065, 327680, 291051, 291051, 4096, 255)

        self.assertEqual({
            'available': 807178240,
            'used': 12158910464-807178240,
            'inodeAvailable': 291051,
            'inodeUsed': 327680-291051,
        }, meter._diskUsage('/'))
        self.assertEqual({
                'Disk space': {
                    '/': {
                        'available': { MEMORY: 807178240 },
                        'used': { MEMORY: 11351732224 },
                        'inodeAvailable': { MEMORY: 291051 },
                        'inodeUsed': { MEMORY: 327680-291051 }
                    }
                }
            }, meter.values())

    def testMeterMultiplePaths(self):
        meter = Diskspace(paths=['/', '/data'])
        meter._vfscall = lambda path: (4096, 4096, 2968484, 197065, 197065, 0, 0, 0, 0, 255)

        self.assertEqual({
            'Disk space': {
                '/': {
                    'available': { MEMORY: 807178240 },
                    'used': { MEMORY: 11351732224 }
                },
                '/data': {
                    'available': { MEMORY: 807178240 },
                    'used': { MEMORY: 11351732224 }
                }
            }
        }, meter.values())

    def testHandleLessLabelsThanPaths(self):
        meter = Diskspace(paths=['/', '/data'], chartLabels=['root'])
        meter._vfscall = lambda path: (4096, 4096, 2968484, 197065, 197065, 0, 0, 0, 0, 255)

        self.assertEqual({
            'Disk space': {
                'root': { 'available': { MEMORY: 807178240 }, 'used': { MEMORY: 11351732224 } },
                '/data': { 'available': { MEMORY: 807178240 }, 'used': { MEMORY: 11351732224 }
                }
            }
        }, meter.values())

    def testHandleUnexistingPaths(self):
        def vfscall(path):
            if path == '/data':
                raise OSError('No such dir.')
            return (4096, 4096, 2968484, 197065, 197065, 0, 0, 0, 0, 255)
        meter = Diskspace(paths=['/', '/data'], chartLabels=['root'])
        meter._vfscall = vfscall
        self.assertEqual({
            'Disk space': {
                'root': { 'available': { MEMORY: 807178240 }, 'used': { MEMORY: 11351732224 } },
                '/data': { 'available': { MEMORY: 0 }, 'used': { MEMORY: 0 }
                }
            }
        }, meter.values())


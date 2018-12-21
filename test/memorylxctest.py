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

from gustos.client import MemoryLxc
from gustos.common.units import MEMORY
from os.path import join

class MemoryLxcTest(SeecrTestCase):
    def testMeter(self):
        VM_NAME = "mock_vm"
        memdir = mkdir(self.tempdir, "sys", "fs", "cgroup", "memory", "lxc", VM_NAME)
        meter = MemoryLxc(root=self.tempdir, hostname=VM_NAME)
        with open(join(memdir, "memory.usage_in_bytes"), "w") as fp:
            fp.write("241614848\n")
        with open(join(memdir, "memory.limit_in_bytes"), "w") as fp:
            fp.write("1073741824\n")
        with open(join(memdir, "memory.stat"), "w") as fp:
            fp.write("cache 211955712\n")


        self.assertEqual({
                'Memory': {
                    'Main memory' : {
                        'free': {
                            MEMORY: 832126976
                        },
                        'cached': {
                            MEMORY: 211955712
                        },
                        'used': {
                            MEMORY: 241614848
                        },
                        'total': {
                            MEMORY: 1073741824
                        }
                    }
                }
            },
            meter.values())

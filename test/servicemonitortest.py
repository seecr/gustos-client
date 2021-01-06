## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2014-2015, 2018 Seecr (Seek You Too B.V.) https://seecr.nl
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
from gustos.client.servicemonitor import ServiceMonitor
from gustos.common.units import PERCENTAGE, MEMORY
from os import makedirs, symlink
from os.path import join

class ServiceMonitorTest(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.serviceDir = join(self.tempdir, 'etc','service')
        makedirs(self.serviceDir)

    def testOneService(self):
        monitor = ServiceMonitor(names=['service-name'], serviceDir=self.serviceDir)
        monitor._findPid = lambda name: 1234
        monitor._measure = lambda pid: (20, 1024)
        self.assertEqual([
                {'CPU usage':
                    {'service-name':
                        {'usage':
                            {PERCENTAGE: 20}
                        }
                    },
                'Memory':
                    {'service-name':
                        {'usage':
                            {MEMORY: 1024}
                        }
                    }
                }], monitor.values())

    def testNoServices(self):
        monitor = ServiceMonitor(names=[], serviceDir=self.serviceDir)
        self.assertEqual(None, monitor.values())

    def testMultipleServices(self):
        monitor = ServiceMonitor(names=['service-name-1', 'service-name-2'], serviceDir=self.serviceDir)
        monitor._findPid = lambda name: 1234
        monitor._measure = lambda pid: (20, 1024)
        self.assertEqual([
                {'CPU usage':
                    {'service-name-1':
                        {'usage':
                            {PERCENTAGE: 20}
                        },
                    },
                'Memory':
                    {'service-name-1':
                        {'usage':
                            {MEMORY: 1024}
                        },
                    }
                },
                {'CPU usage':
                    {'service-name-2':
                        {'usage':
                            {PERCENTAGE: 20}
                        }
                    },
                'Memory':
                    {'service-name-2':
                        {'usage':
                            {MEMORY: 1024}
                        }
                    }
                }], monitor.values())

    def testPidNotFound(self):
        monitor = ServiceMonitor(names=['service-name-1'], serviceDir=self.serviceDir)
        monitor._findPid = lambda name: 1234
        def measure(*args, **kwargs):
            raise IOError("No such file or directory: '/proc/1234/stat'")
        monitor._measure = measure
        self.assertEqual(None, monitor.values())

    def testProcessDisapeared(self):
        monitor = ServiceMonitor(names=['service-name-1'], serviceDir=self.serviceDir)
        monitor._findPid = lambda name: None
        self.assertEqual(None, monitor.values())

    def testOneServiceDown(self):
        monitor = ServiceMonitor(names=['service-name-1', 'service-name-2'], serviceDir=self.serviceDir)
        pids = [None, 1234]
        monitor._findPid = lambda name: pids.pop(0)
        monitor._measure = lambda pid: (20, 1024)
        self.assertEqual([
                {'CPU usage':
                    {'service-name-2':
                        {'usage':
                            {PERCENTAGE: 20}
                        }
                    },
                'Memory':
                    {'service-name-2':
                        {'usage':
                            {MEMORY: 1024}
                        }
                    }
                }], monitor.values())

    def testExcludeServices(self):
        for service in ['A', 'B', 'C']:
            d = join(self.tempdir, 'opt', service)
            makedirs(d)
            symlink(d, join(self.serviceDir, service))
        monitor = ServiceMonitor(excludedNames=['B', 'C'], serviceDir=self.serviceDir)
        pids = [1234]
        monitor._findPid = lambda name: pids.pop(0)
        monitor._measure = lambda pid: (20, 1024)
        self.assertEqual([
                {'CPU usage':
                    {'A':
                        {'usage':
                            {PERCENTAGE: 20}
                        }
                    },
                'Memory':
                    {'A':
                        {'usage':
                            {MEMORY: 1024}
                        }
                    }
                }], monitor.values())

    def testRepr(self):
        self.assertEqual("ServiceMonitor(names=['a', 'b'])", repr(ServiceMonitor(names=['a', 'b'])))
        self.assertEqual("ServiceMonitor(excludedNames=['a', 'b'])", repr(ServiceMonitor(excludedNames=['b', 'a'])))

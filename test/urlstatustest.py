## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2012-2014, 2018, 2021 Seecr (Seek You Too B.V.) https://seecr.nl
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

from gustos.client import UrlStatus
from gustos.common.units import COUNT

from urllib.error import URLError
from seecr.test.io import stdout_replaced

class UrlStatusTest(SeecrTestCase):
    @stdout_replaced
    def testMeter(self):
        meter = UrlStatus(url='http://www.example.org', label="Example.Org")
        meter._urlopen = lambda *args, **kwargs: 200
        self.assertEqual({
            'Url Status': {
                'Example.Org': {
                    'Error': { COUNT: 0 }
                }
            }
        }, meter.values())

        self.assertEqual({
            'Url Status': {
                'Example.Org': {
                    'Error': { COUNT: 0 }
                }
            }
        }, meter.values())

        meter._urlopen = lambda *args, **kwargs: 400
        self.assertEqual({
            'Url Status': {
                'Example.Org': {
                    'Error': { COUNT: 1 },
                }
            }
        }, meter.values())
        meter._urlopen = lambda *args, **kwargs: 501
        self.assertEqual({
            'Url Status': {
                'Example.Org': {
                    'Error': { COUNT: 2 },
                }
            }
        }, meter.values())
        def raiseException(*args, **kwargs):
            raise URLError("some urlopen error")
        meter._urlopen = raiseException
        self.assertEqual({
            'Url Status': {
                'Example.Org': {
                    'Error': { COUNT: 3 },
                }
            }
        }, meter.values())
        meter._urlopen = lambda *args, **kwargs: 200
        self.assertEqual({
            'Url Status': {
                'Example.Org': {
                    'Error': { COUNT: 3 }
                }
            }
        }, meter.values())
        self.assertEqual({
            'Url Status': {
                'Example.Org': {
                    'Error': { COUNT: 3 }
                }
            }
        }, meter.values())
        meter._urlopen = lambda *args, **kwargs: 501
        self.assertEqual({
            'Url Status': {
                'Example.Org': {
                    'Error': { COUNT: 4 },
                }
            }
        }, meter.values())

    def testRepr(self):
        self.assertEqual('UrlStatus(url="http://www.example.org", label="Example.Org", timeout=1)', repr(UrlStatus(url='http://www.example.org', label="Example.Org")))
        self.assertEqual('UrlStatus(url="http://www.example.org", label="Example.Org", timeout=1)', '{}'.format(UrlStatus(url='http://www.example.org', label="Example.Org")))

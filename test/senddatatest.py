## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2023 Seecr (Seek You Too B.V.) https://seecr.nl
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

from gustos.client import SendData


class SendDataTest(SeecrTestCase):
    def testMeter(self):
        (self.tmp_path/'send.this').write_text('{"Backup admin-state": {"Destination seecr11": {"nr_of_backups": {"count": 2}}}}')
        meter = SendData(str(self.tmp_path/'send.this'))
        self.assertEqual({
            "Backup admin-state": {
                "Destination seecr11": {
                    "nr_of_backups": {"count": 2}}}},
            meter.values())

    def testNoFile(self):
        meter = SendData(str(self.tmp_path/'send.this'))
        self.assertEqual(None, meter.values())

    def testBadDataRaisesException(self):
        (self.tmp_path/'send.this').write_text('No json data')
        meter = SendData(str(self.tmp_path/'send.this'))
        self.assertRaises(ValueError, meter.values)

    def testIncompleteDataRaisesException(self):
        (self.tmp_path/'send.this').write_text('{}')
        meter = SendData(str(self.tmp_path/'send.this'))
        self.assertRaises(ValueError, meter.values)
        self.assertRaises(ValueError, meter.validate, {'Group':{}})
        self.assertRaises(ValueError, meter.validate, {'Group':{'Label':{}}})
        self.assertRaises(ValueError, meter.validate, {'Group':{'Label':{'Key':{}}}})
        self.assertRaises(ValueError, meter.validate, {'Group':{'Label':{'Key':{'unit': None}}}})
        meter.validate({'Group':{'Label':{'Key':{'unit': 0}}}})
        self.assertRaises(ValueError, meter.validate, {'':{'Label':{'Key':{'unit': 0}}}})

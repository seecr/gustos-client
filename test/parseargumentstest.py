## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2011-2014, 2018 Seecr (Seek You Too B.V.) https://seecr.nl
# Copyright (C) 2012 Stichting Bibliotheek.nl (BNL) http://www.bibliotheek.nl
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

from unittest import TestCase
from gustos.common import ParseArguments

class ParseArgumentsTest(TestCase):
    def testMandatoryKey(self):
        parser = ParseArguments()
        parser.addOption('', '--name', help='Naam', mandatory=True)
        parser.addOption('', '--port', help='Port', type='int', mandatory=True)
        argv = ['script', '--name', 'TestServer', '--port', '1234']
        options, arguments = parser.parse(argv)
        self.assertEqual(1234, options.port)
        self.assertEqual('TestServer', options.name)
        argv = ['script', '--port', '1234']
        self.assertRaises(ValueError, parser._parse, argv)

    def testAdditionalOptions_optional(self):
        argv = ['script', '--name', 'TestServer']
        parser = ParseArguments()
        parser.addOption('', '--name', help='Naam', mandatory=True)
        parser.addOption('', '--port', help='Port', type='int')
        parser.addOption('', '--withDefault', help='Default', default="default", type='str')
        options, arguments = parser.parse(argv)
        self.assertEqual('TestServer', options.name)
        self.assertEqual(None, options.port)
        self.assertEqual('default', options.withDefault)


## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2012-2014, 2018, 2020, 2023 Seecr (Seek You Too B.V.) https://seecr.nl
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

from gustos.client import FileCount

from gustos.common.units import COUNT
from os.path import join
from os import makedirs

class FileCountTest(SeecrTestCase):
    def test_no_matches(self):
        pattern = join(self.tempdir, "*.txt")
        meter = FileCount(file_pattern=pattern)

        self.assertEqual({
            "File count": {
                pattern: {
                    'files': {COUNT: 0},
                    'directories': {COUNT: 0},
                }
            }
        }, meter.values())

    def test_pattern_for_path_that_doesnt_exist(self):
        try:
            FileCount(file_pattern="/doesnt_exist_at_all/*")
            self.fail()
        except ValueError as e:
            self.assertEqual("No such directory: /doesnt_exist_at_all", str(e))


    def test_with_matches(self):
        pattern = join(self.tempdir, "*.txt")
        open(join(self.tempdir, "a.txt"), "w").close()
        open(join(self.tempdir, "a.doc"), "w").close()
        makedirs(join(self.tempdir, "b.txt"))
        makedirs(join(self.tempdir, "b.xls"))

        meter = FileCount(file_pattern=pattern)

        self.assertEqual({
            "File count": {
                pattern: {
                    'files': {COUNT: 1},
                    'directories': {COUNT: 1},
                }
            }
        }, meter.values())


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

from gustos.common.units import COUNT
from glob import glob
from os.path import isfile, isdir, dirname

class FileCount(object):
    def __init__(self, file_pattern, group='File count'):
        self._file_patterns = file_pattern if type(file_pattern) is list else [file_pattern]
        for pattern in self._file_patterns:
            pattern_dirname = dirname(pattern)
            if not isdir(pattern_dirname):
                raise ValueError(f"No such directory: {pattern_dirname}")

        self._group = group

    def values(self):
        result = { self._group: {} }
        for file_pattern in self._file_patterns:
            matches = glob(file_pattern)
            files = len([match for match in matches if isfile(match)])
            directories = len([match for match in matches if isdir(match)])
            result[self._group][file_pattern] = {"files": {COUNT: files}, "directories": {COUNT: directories}}

        return result

    def __repr__(self):
        return 'FileCount(file_pattern={})'.format(repr(self._file_patterns))

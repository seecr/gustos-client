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

import pathlib
import json

class SendData:
    def __init__(self, path):
        self._path = pathlib.Path(path)
        self.interval = 3600

    def values(self):
        if not self._path.is_file():
            return None
        data = json.loads(self._path.read_text())
        self.validate(data)
        return data

    def validate(self, data):
        if not isinstance(data, list):
            data = [data]
        def not_empty(v):
            if not v:
                raise ValueError('Empty')
        def is_dict(d):
            if not isinstance(d, dict):
                raise ValueError('Expected dict')
            not_empty(d)
        def is_string(d):
            if not isinstance(d, str):
                raise ValueError('Expected str')
            not_empty(d)
        for d in data:
            is_dict(d)
            for group, group_d in d.items():
                is_string(group)
                is_dict(group_d)
                for label, label_d in group_d.items():
                    is_string(label)
                    is_dict(label_d)
                    for key, key_d in label_d.items():
                        is_string(key)
                        is_dict(key_d)
                        for unit, value in key_d.items():
                            is_string(unit)
                            if value is None:
                                raise ValueError('Not none')





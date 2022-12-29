## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2022 Seecr (Seek You Too B.V.) https://seecr.nl
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


import json, pathlib

from ._sslcheck import _SSLCheck

class SSLCertificateCheck(_SSLCheck):
    def __init__(self, configFile, group='sslcheck'):
        _SSLCheck.__init__(self, group)
        self._configFile = pathlib.Path(configFile)

    def findInfo(self):
        if not self._configFile.exists():
            return
        for item in json.loads(self._configFile.read_text()):
            yield {'pem':item.get('pem'), 'hostname': item.get('hostname')}

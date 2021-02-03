## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2019, 2021 Seecr (Seek You Too B.V.) https://seecr.nl
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

from os import walk
from os.path import join
from datetime import datetime
from gustos.common.units import COUNT

from OpenSSL.crypto import load_certificate, FILETYPE_PEM
from ssl import get_server_certificate

def certFromLine(line):
    if not '=' in line:
        return None
    label, value = list(map(str.strip, line.split('=', 1)))
    if label == 'cert' and value.endswith('.pem'):
        return value

class LetsEncryptRenewals(object):
    def __init__(self, renewalsDir='/etc/letsencrypt/renewal', group="letsencrypt"):
        self._renewalsDir = renewalsDir
        self._group = group

    def findPEMs(self):
        for dirpath, dirnames, filenames in walk(self._renewalsDir):
            confFiles = [join(dirpath, filename) for filename in filenames if filename.endswith('.conf')]
            for confFile in confFiles:
                with open(confFile) as fp:
                    for line in [_f for _f in [certFromLine(line) for line in fp.readlines()] if _f]:
                        yield line

    def daysLeftOnPEM(self, filename):
        def daysLeft(cert):
            return (datetime.strptime(cert.get_notAfter().decode(),"%Y%m%d%H%M%SZ").date()-datetime.now().date()).days

        _dl = lambda cert: daysLeft(load_certificate(FILETYPE_PEM, cert))
        with open(filename) as fp:
            daysLeftFile = _dl(fp.read())
        daysLeftServer = _dl(self._get_server_certificate(filename.split('/')[-2]))
        return dict(daysLeftFile=daysLeftFile, daysLeftServer=daysLeftServer)

    def _get_server_certificate(self, hostname):
        return get_server_certificate((hostname, 443))


    def listDaysLeft(self):
        return [dict(pem=pem, **self.daysLeftOnPEM(pem)) for pem in self.findPEMs()]

    def values(self):
        result = { self._group: {} }
        for entry in self.listDaysLeft():
            label = entry['pem'].split('/')[-2]
            result[self._group][label] = dict(days_valid_file={ COUNT: entry['daysLeftFile']}, days_valid_server={ COUNT: entry['daysLeftServer']})
        return result

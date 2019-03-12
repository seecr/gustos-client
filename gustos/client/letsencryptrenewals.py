## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2019 Seecr (Seek You Too B.V.) https://seecr.nl
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

def certFromLine(line):
    if not '=' in line:
        return None
    label, value = map(str.strip, line.split('=', 1))
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
                certLine = filter(None, [certFromLine(line) for line in open(confFile).readlines()])
                for line in certLine:
                    yield line

    def daysLeftOnPEM(self, filename):
        cert = load_certificate(FILETYPE_PEM, open(filename).read())
        return (datetime.strptime(cert.get_notAfter(),"%Y%m%d%H%M%SZ").date()-datetime.now().date()).days

    def listDaysLeft(self):
        return [dict(pem=pem, daysLeft=self.daysLeftOnPEM(pem)) for pem in self.findPEMs()]

    def values(self):
        result = { self._group: {} }
        for entry in self.listDaysLeft():
            label = entry['pem'].split('/')[-2]
            result[self._group][label] = {'days_valid': { COUNT: entry['daysLeft']}}
        return result

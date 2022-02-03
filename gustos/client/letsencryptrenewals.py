## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2019, 2021-2022 Seecr (Seek You Too B.V.) https://seecr.nl
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
import pathlib, configparser, ssl
from ._sslcheck import _SSLCheck


def certInfo(filename):
    try:
        c = configparser.ConfigParser()
        c.read_string('[root]\n' + pathlib.Path(filename).read_text())
        hostnames = [k for k,v in c.items('[webroot_map')]
        return {
            'hostname': hostnames[0],
            'pem': c.get('root', 'cert'),
        }
    except configparser.Error:
        return None

class LetsEncryptRenewals(_SSLCheck):
    def __init__(self, renewalsDir='/etc/letsencrypt/renewal', group="letsencrypt"):
        _SSLCheck.__init__(self, group)
        self._renewalsDir = renewalsDir

    def findInfo(self):
        for dirpath, dirnames, filenames in walk(self._renewalsDir):
            for info in (certInfo(pathlib.Path(dirpath) / n) for n in filenames if n.endswith('.conf')):
                if not info is None:
                    yield info


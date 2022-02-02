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

class LetsEncryptRenewals(object):
    def __init__(self, renewalsDir='/etc/letsencrypt/renewal', group="letsencrypt"):
        self._renewalsDir = renewalsDir
        self._group = group

    def findInfo(self):
        for dirpath, dirnames, filenames in walk(self._renewalsDir):
            for info in (certInfo(pathlib.Path(dirpath) / n) for n in filenames if n.endswith('.conf')):
                if not info is None:
                    yield info

    def daysLeftOnPEM(self, pem, hostname):
        def daysLeft(cert):
            return (datetime.strptime(cert.get_notAfter().decode(),"%Y%m%d%H%M%SZ").date()-datetime.now().date()).days

        _dl = lambda cert: daysLeft(load_certificate(FILETYPE_PEM, cert))
        with open(pem) as fp:
            daysLeftFile = _dl(fp.read())
        daysLeftServer = _dl(self._get_server_certificate(hostname))
        return dict(daysLeftFile=daysLeftFile, daysLeftServer=daysLeftServer)

    def _get_server_certificate(self, hostname):
        conn = ssl.create_connection((hostname, 443))
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        sock = context.wrap_socket(conn, server_hostname=hostname)
        return ssl.DER_cert_to_PEM_cert(sock.getpeercert(True))

    def listDaysLeft(self):
        return [dict(info, **self.daysLeftOnPEM(**info)) for info in self.findInfo()]

    def values(self):
        result = { self._group: {} }
        for entry in self.listDaysLeft():
            label = entry['hostname']
            result[self._group][label] = dict(days_valid_file={ COUNT: entry['daysLeftFile']}, days_valid_server={ COUNT: entry['daysLeftServer']})
        return result

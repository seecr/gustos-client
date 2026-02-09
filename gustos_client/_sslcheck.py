## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2022, 2026 Seecr (Seek You Too B.V.) https://seecr.nl
#
# This file is part of "Gustos-Client"
#
# "Gustos-Client" is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# "Gustos-Client" is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with "Gustos-Client".  If not, see <http://www.gnu.org/licenses/>.
#
## end license ##

from datetime import datetime, timezone
from gustos_common.units import COUNT

from cryptography import x509

from os.path import isfile
import ssl


class _SSLCheck(object):
    def __init__(self, group):
        self._group = group

    def findInfo(self):
        raise NotImplementedError()

    def daysLeftOnPEM(self, pem, hostname):
        def daysLeft(cert):
            return (
                cert.not_valid_after_utc.date() - datetime.now(tz=timezone.utc).date()
            ).days

        result = dict()
        _dl = lambda cert: daysLeft(x509.load_pem_x509_certificate(cert))
        if pem and isfile(pem):
            with open(pem) as fp:
                result["daysLeftFile"] = _dl(fp.read().encode(encoding="utf-8"))
        try:
            result["daysLeftServer"] = _dl(self._get_server_certificate(hostname))
        except:
            raise
            pass
        return result

    def _get_server_certificate(self, hostname):
        conn = ssl.create_connection((hostname, 443))
        context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        sock = context.wrap_socket(conn, server_hostname=hostname)
        return ssl.DER_cert_to_PEM_cert(sock.getpeercert(True))

    def listDaysLeft(self):
        return [dict(info, **self.daysLeftOnPEM(**info)) for info in self.findInfo()]

    def values(self):
        result = {self._group: {}}
        for entry in self.listDaysLeft():
            label = entry["hostname"]
            for key, valuekey in [
                ("days_valid_file", "daysLeftFile"),
                ("days_valid_server", "daysLeftServer"),
            ]:
                value = entry.get(valuekey)
                if value is None:
                    continue
                result[self._group].setdefault(label, {})[key] = {COUNT: value}
        return result

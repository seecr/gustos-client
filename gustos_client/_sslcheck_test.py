## begin license ##
#
# "Gustos" is a monitoring tool by Seecr.
# This client side code for connecting with Gustos server.
#
# Copyright (C) 2026 Seecr (Seek You Too B.V.) https://seecr.nl
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

import gustos_client.testdata as td
from ._sslcheck import _SSLCheck
import datetime

import pytest


def test_ssl_date():
    c = _SSLCheck("test")
    pem = td.path("old_certificate.pem")
    d = datetime.datetime(2025, 6, 1).replace(tzinfo=datetime.timezone.utc)
    cert = c._certificate_file(pem.as_posix())
    assert c._days_left_certificate(cert, now=d) == 188


@pytest.mark.skip(
    reason="This test requires network access and a specific host to be reachable."
)
def test_ssl_host():
    c = _SSLCheck("test")
    c._get_server_certificate("status.vpn.seecr.nl")

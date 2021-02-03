## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2021 Seecr (Seek You Too B.V.) https://seecr.nl
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

from urllib.request import urlopen, Request
from gustos.common.units import COUNT
from gustos.client import VERSION

class UrlStatus(object):
    def __init__(self, url, label="", group="Url Status", timeout=1):
        self._url = url
        self._label = label if label else url
        self._group = group
        self._timeout = timeout
        self._errorCount = 0

    def values(self):
        status = self._getUrlStatus()
        if status >= 400:
            self._errorCount += 1
            print(('Url status %s for url %s' % (status, self._url)))
            from sys import stdout; stdout.flush()
        return {
            self._group: {
                self._label: { 'Error': {COUNT: self._errorCount}}
            }
        }

    def _getUrlStatus(self):
        try:
            return self._urlopen()
        except Exception as e:
            print(("Error for url %s:\n%s" % (self._url, str(e))))
            from sys import stdout; stdout.flush()
            return 1024

    def _urlopen(self):
        request = Request(self._url)
        request.add_header('User-Agent', 'Seecr-Gustos-UrlStatus-%s' % VERSION)
        urlStatus = urlopen(request, timeout=self._timeout)
        result = urlStatus.getcode()
        urlStatus.close()
        return result

    def __repr__(self):
        return 'UrlStatus(url="{}", label="{}", timeout={})'.format(self._url, self._label, self._timeout)

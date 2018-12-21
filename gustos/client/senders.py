## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2012-2014, 2018 Seecr (Seek You Too B.V.) https://seecr.nl
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

from socket import socket, AF_INET, SOCK_DGRAM

class UdpSender(object):
    def __init__(self, host, port, sok=None):
        self._host = host
        self._port = port
        self._sok = sok

    def send(self, data):
        sok = socket(AF_INET, SOCK_DGRAM) if self._sok is None else self._sok
        try:
            sok.sendto(data.encode(), (self._host, self._port))
        finally:
            sok.close()

class TcpSender(object):
    def __init__(self, host, port, sok=None):
        self._host = host
        self._port = port
        self._sok = sok

    def send(self, data):
        # TODO: support hooking into Weightless Reactor if needed
        sok = socket() if self._sok is None else self._sok
        try:
            sok.connect((self._host, self._port))
            sok.settimeout(1.0)
            totalBytesSent = 0
            while totalBytesSent != len(data):
                bytesSent = sok.send(data[totalBytesSent:].encode())
                totalBytesSent += bytesSent
        finally:
            sok.close()

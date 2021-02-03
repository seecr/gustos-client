## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2015, 2018 Seecr (Seek You Too B.V.) https://seecr.nl
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

from gustos.common.units import COUNT
import re
from subprocess import Popen, PIPE
from netaddr import IPNetwork

IPTABLES_LINE = re.compile(r"^\s*(?P<pkts>\d+)\s+(?P<bytes>\d+)\s+(?P<proto>udp|tcp)\s.*?(?P<source>\d+\.\d+\.\d+\.\d+(\/\d+)?)\s+(?P<destination>\d+\.\d+\.\d+\.\d+(\/\d+)?)\s+(udp|tcp)\s+(spt|dpt):(?P<port>\d+)")
IPTABLES_LINE_NO_PORT = re.compile(r"^\s*(?P<pkts>\d+)\s+(?P<bytes>\d+)\s+(?P<proto>all|udp|tcp)\s.*?(?P<source>\d+\.\d+\.\d+\.\d+(\/\d+)?)\s+(?P<destination>\d+\.\d+\.\d+\.\d+(\/\d+)?)")

class Bandwidth(object):
    def __init__(self, chain="MONITOR", group='Bandwidth', resolve=None, domainsToStrip=None):
        self._group = group
        self._chain = chain
        self._resolve = [] if resolve is None else [(IPNetwork(nw), ns) for nw, ns in resolve]
        self._domainsToStrip = [] if domainsToStrip is None else domainsToStrip
        self._dnscache = {}
    
    def resolve(self, ip):
        if not ip in self._dnscache:
            self._dnscache[ip] = self._resolveIp(ip)
        return self._dnscache[ip]

    def _resolveIp(self, ip):
        nameserver = None
        for iprange, ns in self._resolve:
            if ip in iprange:
                nameserver = ns
                break
        result = self._dig(ip, nameserver=nameserver)
        for domain in self._domainsToStrip:
            toStrip = "."+domain
            if result.endswith(toStrip):
                return result[:-len(toStrip)]
        return result

    def _dig(self, ip, nameserver=None):
        arguments = ['dig']
        if nameserver:
            arguments.append("@%s" % nameserver)
        arguments.extend(['+short', "-x", ip])
        process = Popen(arguments, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        result = stdout.decode().strip()
        if result == "":
            return ip
        if result[-1] == '.':
            result = result[:-1]
        return result

    def _readChain(self):
        process = Popen(["iptables", "-L", self._chain, "-nvx"], stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            print(stderr)
            return None
        return stdout.decode().split("\n")

    def values(self):
        lines = self._readChain()
        if not lines:
            raise ValueError("Unable to read iptables chain '%s'" % self._chain)

        matches = []
        for line in lines[2:]:
            match = IPTABLES_LINE.match(line)
            if match:
                matches.append(match.groupdict())
            else:
                match = IPTABLES_LINE_NO_PORT.match(line)
                if match:
                    values = match.groupdict()
                    values['port'] = "*"
                    matches.append(values)

        data = {}
        for match in matches:
            host = match['source']
            if host == '0.0.0.0/0': 
                continue
            if host not in data:
                data[host] = {}
            key = (match['proto'], match['port'])
            if key in data[host]:
                raise ValueError("Key already exists: %s" % str(key))
            data[host][key] = {"OUT": int(match['bytes'])}

        for match in matches:
            host = match['destination']
            if match['destination'] == '0.0.0.0/0': 
                continue
            if not host in data:
                raise ValueError("Key does not exists: %s" % str(key))
            key = (match['proto'], match['port'])
            data[host][key]["IN"] = int(match['bytes'])

        results = []
        for host, ports in list(data.items()):
            portData = {}
            for (protocol, port), counts in list(ports.items()):
                if protocol == 'all' and port == "*":
                    key = self.resolve(host)
                else:
                    key = '%s - %s %s' % (self.resolve(host), protocol, port)
                portData[key] = {
                    'IN': { COUNT: counts['IN']},
                    'OUT': { COUNT: counts['OUT']}
                }
            results.append({'Bandwidth': portData})
        return results

    def __repr__(self):
        return 'Bandwidth()'

## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2024 Seecr (Seek You Too B.V.) https://seecr.nl
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

import subprocess
import re

from gustos.common.units import COUNT

down_re = re.compile("/etc/service/lxc-(?P<vm>[^:].*): down (?P<seconds>[0-9]+) seconds$")
down_up_re = re.compile("/etc/service/lxc-(?P<vm>[^:].*): down (?P<seconds>[0-9]+) seconds, normally up$")
up_re = re.compile("/etc/service/lxc-(?P<vm>[^:].*): up \(pid [0-9]+\) (?P<seconds>[0-9]+) seconds")

class LxcUptime:
    def __init__(self, svstat_command=None):
        self._svstat_command = svstat_command or svstat

    def values(self):
        status, uptimes, downtimes = parse_svstat(self._svstat_command())
        return dict(
            LXC=dict(
                Uptimes={k:{COUNT:int(v)} for k,v in uptimes.items()},
                Downtimes={k:{COUNT:int(v)} for k,v in downtimes.items()},
                Status={k:{COUNT:v} for k,v in status.items()}
            )
        )


def svstat():
    result = subprocess.run("svstat /etc/service/lxc-*", capture_output=True, text=True, shell=True)
    return result.stdout.strip()

def parse_svstat(output):
    stats = {"up":0, "down": 0, "down-up": 0}
    uptimes = {}
    downtimes = {}
    for line in output.strip().split("\n"):
        match = down_re.match(line)
        if match is not None:
            stats['down'] += 1
            uptimes[match.groupdict()['vm']] = 0
            downtimes[match.groupdict()['vm']] = match.groupdict()['seconds']
            continue

        match = up_re.match(line)
        if match is not None:
            stats['up'] += 1
            uptimes[match.groupdict()['vm']] = match.groupdict()['seconds']
            downtimes[match.groupdict()['vm']] = 0
            continue

        match = down_up_re.match(line)
        if match is not None:
            stats['down-up'] += 1
            uptimes[match.groupdict()['vm']] = 0
            downtimes[match.groupdict()['vm']] = match.groupdict()['seconds']
            continue
        print("Unknwon line: [", line, "]")

    return stats, uptimes, downtimes

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

from gustos.common.units import MEMORY


KB = 1024


class Memory(object):
    def __init__(self, group="Memory", chartLabel="Main memory", disabled=None):
        self._group = group
        self._chartLabel = chartLabel
        self._disabled = disabled or tuple()

    def values(self):
        total, memUsage = self._memoryUsage()
        if "remaining" not in self._disabled:
            memUsage["remaining"] = {
                MEMORY: total
                - sum([v for d in list(memUsage.values()) for v in list(d.values())])
            }

        if "available" not in self._disabled:
            if all(name in memUsage for name in ["free", "buffers", "cached"]):
                memUsage["available"] = {
                    MEMORY: memUsage["free"][MEMORY]
                    + memUsage["buffers"][MEMORY]
                    + memUsage["cached"][MEMORY]
                }

        return {self._group: {self._chartLabel: memUsage}}

    def _memoryUsage(self):
        memInfo = self._readProcMeminfo()
        infoDict = {}
        for k, v in [
            ("free", "MemFree"),
            ("slab", "Slab"),
            ("buffers", "Buffers"),
            ("cached", "Cached"),
        ]:
            if k in self._disabled:
                continue
            if v in memInfo:
                infoDict[k] = {MEMORY: memInfo[v] * KB}
        return memInfo["MemTotal"] * KB, infoDict

    def _readProcMeminfo(self):
        return dict(
            [
                (k, int(v.strip().split()[0]))
                for k, v in (
                    line.split(":", 1) for line in open("/proc/meminfo").readlines()
                )
            ]
        )

    def __repr__(self):
        return "Memory()"

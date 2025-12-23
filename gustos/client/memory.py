## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2012-2014, 2018, 2025 Seecr (Seek You Too B.V.) https://seecr.nl
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
from ._utils import validate_enabled


KB = 1024

KEY_REMAINING = "remaining"
KEY_AVAILABLE = "available"
KEY_FREE = "free"
KEY_SLAB = "slab"
KEY_BUFFERS = "buffers"
KEY_CACHED = "cached"

KEYS = {KEY_REMAINING, KEY_AVAILABLE, KEY_FREE, KEY_SLAB, KEY_BUFFERS, KEY_CACHED}


class Memory(object):
    def __init__(self, group="Memory", chartLabel="Main memory", enabled=None):
        self._group = group
        self._chartLabel = chartLabel
        self._enabled = validate_enabled(enabled, KEYS)

    def _is_enabled(self, name):
        if len(self._enabled) == 0:
            return True
        return name in self._enabled

    def values(self):
        total, memUsage = self._memoryUsage()
        if self._is_enabled(KEY_REMAINING):
            memUsage[KEY_REMAINING] = {
                MEMORY: total
                - sum([v for d in list(memUsage.values()) for v in list(d.values())])
            }

        if self._is_enabled(KEY_AVAILABLE):
            if all(name in memUsage for name in [KEY_FREE, KEY_BUFFERS, KEY_CACHED]):
                memUsage[KEY_AVAILABLE] = {
                    MEMORY: memUsage[KEY_FREE][MEMORY]
                    + memUsage[KEY_BUFFERS][MEMORY]
                    + memUsage[KEY_CACHED][MEMORY]
                }

        return {self._group: {self._chartLabel: memUsage}}

    def _memoryUsage(self):
        memInfo = self._readProcMeminfo()
        infoDict = {}
        for k, v in [
            (KEY_FREE, "MemFree"),
            (KEY_SLAB, "Slab"),
            (KEY_BUFFERS, "Buffers"),
            (KEY_CACHED, "Cached"),
        ]:
            if self._is_enabled(k):
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

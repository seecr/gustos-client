## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2012-2014, 2018, 2020 Seecr (Seek You Too B.V.) https://seecr.nl
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

from os import statvfs
from gustos.common.units import MEMORY


class Diskspace(object):
    def __init__(
        self,
        path="/",
        paths=None,
        group="Disk space",
        chartLabel=None,
        chartLabels=None,
        disabled=None,
    ):
        self._paths = paths if paths else [path]
        self._group = group
        self._chartLabels = chartLabels if chartLabels else chartLabel or self._paths
        self._disabled = disabled or tuple()

    def values(self):
        result = {self._group: {}}
        for i, path in enumerate(self._paths):
            diskUsage = self._diskUsage(path)
            label = self._chartLabels[i] if i < len(self._chartLabels) else path
            chartData = dict(
                (key, {MEMORY: value})
                for (key, value) in list(diskUsage.items())
                if key not in self._disabled
            )
            result[self._group][label] = chartData
        return result

    def _diskUsage(self, path):
        try:
            (
                f_bsize,
                f_frsize,
                f_blocks,
                f_bfree,
                f_bavail,
                f_files,
                f_ffree,
                f_favail,
                f_flag,
                f_namemax,
            ) = self._vfscall(path)
            values = {
                "available": f_bsize * f_bavail,
                "used": (f_blocks - f_bavail) * f_bsize,
            }
            if f_files != 0:
                values["inodeAvailable"] = f_favail
                values["inodeUsed"] = f_files - f_favail

            return values
        except OSError:
            return {"available": 0, "used": 0}

    def _vfscall(self, path):
        return statvfs(path)

    def __repr__(self):
        return "Diskspace(paths={})".format(repr(self._paths))

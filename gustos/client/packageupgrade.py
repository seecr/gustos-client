## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2012-2015, 2018 Seecr (Seek You Too B.V.) https://seecr.nl
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

from traceback import print_exc
from gustos.common.units import COUNT
from os.path import isfile
from subprocess import Popen, PIPE
from distutils.version import LooseVersion
import sys

class RedhatPackages(object):
    def values(self):
        process = Popen(["yum", "makecache"], stdout=PIPE, stderr=PIPE)
        pOut, pErr = process.communicate()
        if process.returncode != 0:
            raise RuntimeError("Error while updating yum:" + pErr)

        process = Popen(["yum", "--quiet", "updateinfo", "list", "sec"], stdout=PIPE, stderr=PIPE)
        pOut, pErr = process.communicate()
        if process.returncode != 0:
            raise RuntimeError("Error during yum updateinfo:" + pErr)
        return 0 if len(pOut.strip()) == 0 else len(pOut.strip().split("\n"))

class DebianPackages(object):
    def __init__(self, cache=None):
        if cache is None:
            from apt import Cache
            cache = Cache()
        self._cache = cache

    def values(self):
        self._cache.update()
        self._cache.open()

        counts=dict(packages=0, security=0)
        for pkg in self._cache:
            if pkg.is_installed and pkg.is_upgradable:
                for origin in pkg.candidate.origins:
                    if origin.site == 'security.debian.org':
                        counts['security'] += 1
                    else:
                        counts['packages'] += 1
        return counts

class PackageUpgrade(object):

    def __init__(self, packages=None):
        if packages is None:
            if isfile("/etc/debian_version"):
                self._packages = DebianPackages()
            elif isfile("/etc/redhat-release"):
                self._packages = RedhatPackages()
            else:
                raise RuntimeError("Unknown Linux Distribution")
        else:
            self._packages = packages

    def values(self):
        availableUpdates = self._packages.values()
        result = dict(Upgrades={k.capitalize():dict(available={COUNT: v}) for k,v in availableUpdates.items()})

        return result

    def __repr__(self):
        return 'SecurityUpdates()'



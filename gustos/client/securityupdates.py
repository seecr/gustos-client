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

def _security_updates(countMethod):
    import sys                                          #DO_NOT_DISTRIBUTE
    env = dict(PYTHONPATH=':'.join(sys.path))           #DO_NOT_DISTRIBUTE

    stdout, stderr = Popen(
        [sys.executable, "-c", "from gustos.client.securityupdates import {0}; print({0}())".format(countMethod)],
        stdout=PIPE,
        stderr=PIPE,
        env=env                                         #DO_NOT_DISTRIBUTE
        ).communicate()
    try:
        return int(stdout.strip())
    except:
        raise ValueError("SecurityUpdatesError(stdout=%s, stderr=%s)"%(repr(stdout), repr(stderr)))

def debian_security_updates():
    return _security_updates(countMethod="count_debian_security_updates")

def count_debian_security_updates():
    from apt import Cache

    cache = Cache()
    try:
        cache.update()
        cache.open()

        count = 0
        for pkg in cache:
            if pkg.is_upgradable:
                for origin in pkg.candidate.origins:
                    if origin.site == 'security.debian.org':
                        count += 1
        return count
    finally:
        cache = None

def count_redhat_security_updates():
    process = Popen(["yum", "makecache"], stdout=PIPE, stderr=PIPE)
    pOut, pErr = process.communicate()
    if process.returncode != 0:
        raise RuntimeError("Error while updating yum:" + pErr)

    process = Popen(["yum", "--quiet", "updateinfo", "list", "sec"], stdout=PIPE, stderr=PIPE)
    pOut, pErr = process.communicate()
    if process.returncode != 0:
        raise RuntimeError("Error during yum updateinfo:" + pErr)
    return 0 if len(pOut.strip()) == 0 else len(pOut.strip().split("\n"))

class SecurityUpdates(object):

    def __init__(self):
        if isfile("/etc/debian_version"):
            self._countSecurityUpdates = debian_security_updates
        elif isfile("/etc/redhat-release"):
            self._countSecurityUpdates = count_redhat_security_updates
        else:
            raise RuntimeError("Unknown Linux Distribution")

    def values(self):
        availableUpdates = self._countSecurityUpdates()
        return {
            'Updates': {
                'Security': {
                    'available': {
                        COUNT: availableUpdates
                    },
                }
            }
        }

    def __repr__(self):
        return 'SecurityUpdates()'



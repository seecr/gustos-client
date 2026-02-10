## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
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

from seecr.test import SeecrTestCase

from gustos_client import PackageUpgrade
from gustos_client.packageupgrade import DebianPackages

class Dict(dict):
    def __getattribute__(self, key):
        if key in self:
            return self[key]
        return dict.__getattribute__(self, key)

    def __setattr__(self, key, value):
        self[key] = value

class MockCache(object):
    def __init__(self, packages):
        self._packages = packages
    def open(self): pass
    def update(self): pass
    def __iter__(self):
        return iter(self._packages)

class PackageUpgradeTest(SeecrTestCase):
    def testNoUpgrades(self):
        cache = MockCache(packages=[])
        packages = DebianPackages(cache=cache)

        p = PackageUpgrade(packages=DebianPackages(cache=cache))
        self.assertEqual({'Upgrades': {
            'Security': {'available': {'count': 0}},
            'Packages': {'available': {'count': 0}},
        }}, p.values())

    def testSecurityUpgrades(self):
        cache = MockCache(packages=[
            Dict(
                is_upgradable=True,
                is_installed=True,
                candidate=Dict(
                    origins=[
                        Dict(site='security.debian.org'),
                    ]
                )
            )
        ])
        packages = DebianPackages(cache=cache)

        p = PackageUpgrade(packages=DebianPackages(cache=cache))
        self.assertEqual({'Upgrades': {
            'Security': {'available': {'count': 1}},
            'Packages': {'available': {'count': 0}},
        }}, p.values())

    def testSecurityUpgradesForInstalled(self):
        cache = MockCache(packages=[
            Dict(
                is_upgradable=True,
                is_installed=False,
                candidate=Dict(
                    origins=[
                        Dict(site='security.debian.org'),
                    ]
                )
            )
        ])
        packages = DebianPackages(cache=cache)

        p = PackageUpgrade(packages=DebianPackages(cache=cache))
        self.assertEqual({'Upgrades': {
            'Security': {'available': {'count': 0}},
            'Packages': {'available': {'count': 0}},
        }}, p.values())

    def testAllUpgradesAvailable(self):
        cache = MockCache(packages=[
            Dict(
                is_upgradable=True,
                is_installed=True,
                candidate=Dict(
                    origins=[
                        Dict(site='security.debian.org'),
                    ]
                )
            ),
            Dict(
                is_upgradable=True,
                is_installed=True,
                candidate=Dict(
                    origins=[
                        Dict(site='repository.vpn.seecr.nl'),
                    ]
                )
            ),
            Dict(
                is_upgradable=True,
                is_installed=False,
                candidate=Dict(
                    origins=[
                        Dict(site='repository.vpn.seecr.nl'),
                    ]
                )
            )
        ])
        packages = DebianPackages(cache=cache)

        p = PackageUpgrade(packages=DebianPackages(cache=cache))
        self.assertEqual({
            'Upgrades': {
                'Security': { 'available': { 'count': 1 } },
                'Packages': { 'available': { 'count': 1 } }
            }
        }, p.values())

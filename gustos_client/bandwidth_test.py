## begin license ##
#
# "Gustos" is a monitoring tool by Seecr.
# This client side code for connecting with Gustos server.
#
# Copyright (C) 2012-2014, 2018, 2021, 2026 Seecr (Seek You Too B.V.) https://seecr.nl
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
# flake8: noqa E501

from gustos_client import Bandwidth
from gustos_common.units import COUNT

DNS = {
    "212.110.171.149": "a.vpn.seecr.nl",
    "212.110.171.146": "wiki.seecr.nl",
    "212.110.171.145": "hbo.dev.seecr.nl",
}


def test_meter():
    meter = Bandwidth(chain="MONITOR", domainsToStrip=["seecr.nl"])
    OUTPUT = """Chain MONITOR (6 references)
    pkts      bytes target     prot opt in     out     source               destination
    6762   617365            udp  --  *      *       212.110.171.149      0.0.0.0/0            udp spt:1195
    6792   644497            udp  --  *      *       0.0.0.0/0            212.110.171.149      udp dpt:1195
   58957 15282597            udp  --  *      *       212.110.171.149      0.0.0.0/0            udp spt:1194
   33368  3102571            udp  --  *      *       0.0.0.0/0            212.110.171.149      udp dpt:1194
     614   439921            tcp  --  *      *       212.110.171.146      0.0.0.0/0            tcp spt:443
     793    80275            tcp  --  *      *       0.0.0.0/0            212.110.171.146      tcp dpt:443
     898   830941            tcp  --  *      *       212.110.171.145      0.0.0.0/0            tcp spt:443
    1099   167857            tcp  --  *      *       0.0.0.0/0            212.110.171.145      tcp dpt:443"""

    meter._readChain = lambda: OUTPUT.split("\n")
    meter._dig = lambda ip, **kwargs: DNS.get(ip)

    expected = [
        {
            "Bandwidth": {
                "a.vpn - udp 1195": {
                    "In": {COUNT: 644497},
                    "Out": {COUNT: 617365},
                },
                "a.vpn - udp 1194": {
                    "In": {COUNT: 3102571},
                    "Out": {COUNT: 15282597},
                },
            },
        },
        {
            "Bandwidth": {
                "wiki - tcp 443": {
                    "In": {COUNT: 80275},
                    "Out": {COUNT: 439921},
                }
            }
        },
        {
            "Bandwidth": {
                "hbo.dev - tcp 443": {
                    "In": {COUNT: 167857},
                    "Out": {COUNT: 830941},
                },
            }
        },
    ]
    assert sorted(
        [sorted(item["Bandwidth"].keys()) for item in list(meter.values())]
    ) == [
        ["a.vpn - udp 1194", "a.vpn - udp 1195"],
        ["hbo.dev - tcp 443"],
        ["wiki - tcp 443"],
    ]


def test_no_ports():
    meter = Bandwidth(chain="MONITOR", domainsToStrip=["seecr.nl"])
    OUTPUT = """Chain MONITOR (6 references)
    pkts      bytes target     prot opt in     out     source               destination
      14     4516            all  --  *      *       212.110.171.150      0.0.0.0/0
       8      496            all  --  *      *       0.0.0.0/0            212.110.171.150
       3      243            udp  --  *      *       212.110.171.149      0.0.0.0/0            udp spt:1195
       3      243            udp  --  *      *       0.0.0.0/0            212.110.171.149      udp dpt:1195"""

    meter._readChain = lambda: OUTPUT.split("\n")
    assert len(list(meter.values())) == 2


def test_resolve_with_nameserver():
    meter = Bandwidth(chain="MONITOR", resolve=[("10.9.0.0/16", "a.ns.seecr.nl")])
    arguments = []

    def _dig(*args, **kwargs):
        arguments.append((args, kwargs))
        return "some.domain.name."

    meter._dig = _dig
    meter.resolve("10.9.6.1")
    assert arguments == [(("10.9.6.1",), {"nameserver": "a.ns.seecr.nl"})]

    arguments = []
    meter.resolve("10.8.6.1")
    assert arguments == [(("10.8.6.1",), {"nameserver": None})]


def test_resolve_strip_domain():
    meter = Bandwidth(chain="MONITOR", domainsToStrip=["seecr.nl"])
    meter._dig = lambda *args, **kwargs: "test.seecr.nl"

    assert meter.resolve("1.2.3.4") == "test"
    meter._dig = lambda *args, **kwargs: "test.cq2.nl"

    assert meter.resolve("1.2.3.5") == "test.cq2.nl"
    assert meter._dnscache == {"1.2.3.4": "test", "1.2.3.5": "test.cq2.nl"}

## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2019, 2021-2022, 2026 Seecr (Seek You Too B.V.) https://seecr.nl
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
from seecr.test.utils import mkdir

from os.path import join
from datetime import datetime, timedelta, timezone
import pathlib, json

from gustos_client import LetsEncryptRenewals, SSLCertificateCheck

dataPath = pathlib.Path(__file__).parent / "data"


def writeFile(filename, contents, mode="w"):
    with open(filename, mode) as fp:
        fp.write(contents)


class LetsEncryptRenewalsTest(SeecrTestCase):
    def testFindPEMs(self):
        ler = LetsEncryptRenewals(renewalsDir=join(self.tempdir, "does_not_exist"))
        self.assertEqual([], list(ler.findInfo()))

        writeFile(join(self.tempdir, "some_file"), "nothing in here")
        writeFile(join(self.tempdir, "some_file.conf"), "nothing in here either")
        writeFile(
            join(self.tempdir, "this.conf"), "cert = This is not the one you seek"
        )
        writeFile(
            join(self.tempdir, "this_one.conf"),
            "cert = /path/to/certificate/file.pem\n",
        )
        writeFile(
            join(self.tempdir, "this_two.conf"),
            "cert = /path/to/certificate/file.pem\n[[webroot_map]]\nexample.com = /var/www/html\n",
        )

        ler = LetsEncryptRenewals(renewalsDir=self.tempdir)
        self.assertEqual(
            [{"hostname": "example.com", "pem": "/path/to/certificate/file.pem"}],
            list(ler.findInfo()),
        )

    def testNoPemNoData(self):
        configForSslCheck = [{"pem": "/does/not/exist", "hostname": "host.name"}]
        configFileForSslCheck = pathlib.Path(self.tempdir) / "sslcheck.conf"
        configFileForSslCheck.write_text(json.dumps(configForSslCheck))
        check = SSLCertificateCheck(configFileForSslCheck)
        check._get_server_certificate = lambda hostname: create_cert(42)
        self.assertEqual(
            dict(sslcheck={"host.name": {"days_valid_server": {"count": 42}}}),
            check.values(),
        )

    def testFindDaysLeft(self):
        confDir = mkdir(self.tempdir, "conf")
        certDir = mkdir(self.tempdir, "cert")

        expectedDaysLeft = []
        meters = dict()
        configForSslCheck = []
        for name, hostnames, daysLeftFile, daysLeftServer in [
            ("aap", ["aap.nl"], 5, 5),
            ("noot", ["noot.nl"], 12, 5),
            ("mies", ["mies.nl", "vuur.nl"], 90, 5),
        ]:
            hostname = hostnames[0]
            mkdir(certDir, name)
            certFile = join(certDir, name, "cert.pem")
            expectedDaysLeft.append(
                dict(
                    pem=certFile,
                    hostname=hostname,
                    daysLeftFile=daysLeftFile,
                    daysLeftServer=daysLeftServer,
                )
            )
            meters[hostname] = dict(
                days_valid_file=dict(count=daysLeftFile),
                days_valid_server=dict(count=daysLeftServer),
            )
            webroot = "\n".join(f"{hn} = /var/www/html" for hn in hostnames)
            writeFile(
                join(confDir, "{}.conf".format(name)),
                "cert = {}\n[[webroot_map]]\n{}".format(certFile, webroot),
            )
            configForSslCheck.append(dict(pem=certFile, hostname=hostname))
            writeFile(certFile, create_cert(daysValid=daysLeftFile), mode="wb")
        configFileForSslCheck = pathlib.Path(self.tempdir) / "sslcheck.conf"
        configFileForSslCheck.write_text(json.dumps(configForSslCheck))

        ler = LetsEncryptRenewals(renewalsDir=confDir)
        ler._get_server_certificate = lambda hostname: create_cert(5)
        self.assertEqual(
            sorted(expectedDaysLeft, key=lambda each: each["pem"]),
            sorted(ler.listDaysLeft(), key=lambda each: each["pem"]),
        )
        self.assertEqual(dict(letsencrypt=meters), ler.values())

        sslc = SSLCertificateCheck(str(configFileForSslCheck))
        sslc._get_server_certificate = lambda hostname: create_cert(5)
        self.assertEqual(
            sorted(expectedDaysLeft, key=lambda each: each["pem"]),
            sorted(sslc.listDaysLeft(), key=lambda each: each["pem"]),
        )
        self.assertEqual(dict(sslcheck=meters), sslc.values())


def create_cert(daysValid):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes

    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, "My Test Certificate"),
        ]
    )

    now = datetime.now(tz=timezone.utc)

    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(private_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + timedelta(days=daysValid))
        .sign(private_key, hashes.SHA256())
    )

    return cert.public_bytes(serialization.Encoding.PEM)


def test_find_info(tmp_path):
    data_path = tmp_path / "data"
    data_path.mkdir()
    data_path.joinpath("example_com-cert.conf").write_text(
        """
# renew_before_expiry = 30 days
version = 0.31.0
archive_dir = /etc/letsencrypt/archive/example_com-cert
cert = /etc/letsencrypt/live/example_com-cert/cert.pem
privkey = /etc/letsencrypt/live/example_com-cert/privkey.pem
chain = /etc/letsencrypt/live/example_com-cert/chain.pem
fullchain = /etc/letsencrypt/live/example_com-cert/fullchain.pem

# Options used in the renewal process
[renewalparams]
account = account_number
authenticator = webroot
server = https://letsencrypt.example.org/directory
renew_hook = /usr/bin/restart-script
[[webroot_map]]
example.com = /var/www/html
sub.example.com = /var/www/html
"""
    )
    ler = LetsEncryptRenewals(renewalsDir=str(data_path))
    assert list(ler.findInfo()) == [
        {
            "hostname": "example.com",
            "pem": "/etc/letsencrypt/live/example_com-cert/cert.pem",
        }
    ]

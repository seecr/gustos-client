## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2019, 2021-2022 Seecr (Seek You Too B.V.) https://seecr.nl
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

from seecr.test import SeecrTestCase
from seecr.test.utils import mkdir

from os.path import join
from datetime import datetime, timedelta
import pathlib

from gustos.client import LetsEncryptRenewals

dataPath = pathlib.Path(__file__).parent / 'data'

def writeFile(filename, contents, mode="w"):
    with open(filename, mode) as fp:
        fp.write(contents)

class LetsEncryptRenewalsTest(SeecrTestCase):
    def testFindPEMs(self):
        ler = LetsEncryptRenewals(renewalsDir=join(self.tempdir, 'does_not_exist'))
        self.assertEqual([], list(ler.findInfo()))

        writeFile(join(self.tempdir, "some_file"), "nothing in here")
        writeFile(join(self.tempdir, "some_file.conf"), "nothing in here either")
        writeFile(join(self.tempdir, "this.conf"), "cert = This is not the one you seek")
        writeFile(join(self.tempdir, "this_one.conf"), "cert = /path/to/certificate/file.pem\n")
        writeFile(join(self.tempdir, "this_two.conf"), "cert = /path/to/certificate/file.pem\n[[webroot_map]]\nexample.com = /var/www/html\n")

        ler = LetsEncryptRenewals(renewalsDir=self.tempdir)
        self.assertEqual([{'hostname': 'example.com', 'pem': '/path/to/certificate/file.pem'}], list(ler.findInfo()))

    def testFindInfo(self):
        ler = LetsEncryptRenewals(renewalsDir=str(dataPath))
        self.assertEqual([{'hostname': 'example.com','pem': '/etc/letsencrypt/live/example_com-cert/cert.pem'}], list(ler.findInfo()))

    def testFindDaysLeft(self):
        confDir = mkdir(self.tempdir, "conf")
        certDir = mkdir(self.tempdir, "cert")

        expectedDaysLeft = []
        meters = dict()
        for name, hostnames, daysLeftFile, daysLeftServer in [
                ( 'aap', ['aap.nl'],              5, 5),
                ('noot', ['noot.nl'],             12, 5),
                ('mies', ['mies.nl', 'vuur.nl'], 90, 5)]:
            hostname = hostnames[0]
            mkdir(certDir, name)
            certFile = join(certDir, name, 'cert.pem')
            expectedDaysLeft.append(dict(pem=certFile, hostname=hostname, daysLeftFile=daysLeftFile, daysLeftServer=daysLeftServer))
            meters[hostname] = dict(
                days_valid_file=dict(
                    count=daysLeftFile),
                days_valid_server=dict(
                    count=daysLeftServer))
            webroot = '\n'.join(f'{hn} = /var/www/html' for hn in hostnames)
            writeFile(join(confDir, "{}.conf".format(name)), "cert = {}\n[[webroot_map]]\n{}".format(certFile, webroot))
            writeFile(certFile, create_cert(daysValid=daysLeftFile), mode="wb")

        ler = LetsEncryptRenewals(renewalsDir=confDir)
        ler._get_server_certificate = lambda hostname: create_cert(5)
        self.assertEqual(sorted(expectedDaysLeft, key=lambda each: each['pem']), sorted(ler.listDaysLeft(), key=lambda each: each['pem']))
        self.assertEqual(dict(letsencrypt=meters), ler.values())


def create_cert(daysValid):
    from OpenSSL.crypto import PKey, TYPE_RSA, X509Req, X509, dump_certificate, FILETYPE_PEM

    privkey = PKey()
    privkey.generate_key(TYPE_RSA, 2048)

    cert_req = X509Req()
    cert_req.get_subject().OU = "My Test Certificate"
    cert_req.set_pubkey(privkey)

    cert = X509()
    cert.set_notBefore(datetime.now().strftime("%Y%m%d%H%M%SZ").encode())
    cert.set_notAfter((datetime.now()+timedelta(days=daysValid)).strftime("%Y%m%d%H%M%SZ").encode())
    cert.set_pubkey(cert_req.get_pubkey())
    cert.sign(privkey, 'sha256')
    return dump_certificate(FILETYPE_PEM, cert)

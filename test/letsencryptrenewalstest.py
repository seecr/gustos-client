## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2019, 2021 Seecr (Seek You Too B.V.) https://seecr.nl
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

from gustos.client import LetsEncryptRenewals

def writeFile(filename, contents, mode="w"):
    with open(filename, mode) as fp:
        fp.write(contents)

class LetsEncryptRenewalsTest(SeecrTestCase):
    def testFindPEMs(self):
        ler = LetsEncryptRenewals(renewalsDir=join(self.tempdir, 'does_not_exist'))
        self.assertEqual([], list(ler.findPEMs()))

        writeFile(join(self.tempdir, "some_file"), "nothing in here")
        writeFile(join(self.tempdir, "some_file.conf"), "nothing in here either")
        writeFile(join(self.tempdir, "this.conf"), "cert = This is not the one you seek")
        writeFile(join(self.tempdir, "this_one.conf"), "cert = /path/to/certificate/file.pem")

        ler = LetsEncryptRenewals(renewalsDir=self.tempdir)
        self.assertEqual(['/path/to/certificate/file.pem'], list(ler.findPEMs()))

    def testFindDaysLeft(self):
        confDir = mkdir(self.tempdir, "conf")
        certDir = mkdir(self.tempdir, "cert")

        expectedDaysLeft = []
        meters = dict()
        for name, daysLeftFile, daysLeftServer in [('aap', 5, 5), ('noot', 12, 5), ('mies', 90, 5)]:
            mkdir(certDir, name)
            certFile = join(certDir, name, 'cert.pem')
            expectedDaysLeft.append(dict(pem=certFile, daysLeftFile=daysLeftFile, daysLeftServer=daysLeftServer))
            meters[name] = dict(
                days_valid_file=dict(
                    count=daysLeftFile), 
                days_valid_server=dict(
                    count=daysLeftServer))
            writeFile(join(confDir, "{}.conf".format(name)), "cert = {}".format(certFile))
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

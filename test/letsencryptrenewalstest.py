## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2019 Seecr (Seek You Too B.V.) https://seecr.nl
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

class LetsEncryptRenewalsTest(SeecrTestCase):
    def testFindPEMs(self):
        ler = LetsEncryptRenewals(renewalsDir=join(self.tempdir, 'does_not_exist'))
        self.assertEqual([], list(ler.findPEMs()))

        open(join(self.tempdir, "some_file"), "w").write("nothing in here")
        open(join(self.tempdir, "some_file.conf"), "w").write("nothing in here either")
        open(join(self.tempdir, "this.conf"), "w").write("cert = This is not the one you seek")
        open(join(self.tempdir, "this_one.conf"), "w").write("cert = /path/to/certificate/file.pem")

        ler = LetsEncryptRenewals(renewalsDir=self.tempdir)
        self.assertEqual(['/path/to/certificate/file.pem'], list(ler.findPEMs()))

    def testFindDaysLeft(self):
        confDir = mkdir(self.tempdir, "conf")
        certDir = mkdir(self.tempdir, "cert")

        expectedDaysLeft = []
        meters = dict()
        for name, days in [('aap', 5), ('noot', 12), ('mies', 90)]:
            mkdir(certDir, name)
            certFile = join(certDir, name, 'cert.pem')
            expectedDaysLeft.append(dict(pem=certFile, daysLeft=days))
            meters[name] = dict(days_valid=dict(count=days))
            open(join(confDir, "{}.conf".format(name)), "w").write("cert = {}".format(certFile))
            open(certFile, "w").write(create_cert(daysValid=days))

        ler = LetsEncryptRenewals(renewalsDir=confDir)
        self.assertEqual(sorted(expectedDaysLeft), sorted(ler.listDaysLeft()))
        self.assertEqual(dict(letsencrypt=meters), ler.values())


def create_cert(daysValid):
    from OpenSSL.crypto import PKey, TYPE_RSA, X509Req, X509, dump_certificate, FILETYPE_PEM

    privkey = PKey()
    privkey.generate_key(TYPE_RSA, 2048)

    cert_req = X509Req()
    cert_req.get_subject().OU = "My Test Certificate"
    cert_req.set_pubkey(privkey)

    cert = X509()
    cert.set_notBefore(datetime.now().strftime("%Y%m%d%H%M%SZ"))
    cert.set_notAfter((datetime.now()+timedelta(days=daysValid)).strftime("%Y%m%d%H%M%SZ"))
    cert.set_pubkey(cert_req.get_pubkey())
    cert.sign(privkey, 'sha256')
    return dump_certificate(FILETYPE_PEM, cert)

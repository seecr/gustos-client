#!/usr/bin/env python
## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2011-2014, 2018-2019, 2023 Seecr (Seek You Too B.V.) https://seecr.nl
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

import os, sys
os.system('find .. -name "*.pyc" | xargs rm -f')

from glob import glob
for path in glob('../deps.d/*'):
    sys.path.insert(0, path)

sys.path.insert(0, '../../common')
sys.path.insert(0, '..')

from unittest import main

from bandwidthtest import BandwidthTest
from clienttest import ClientTest
from cpuusagelxctest import CpuUsageLxcTest
from cpuusagetest import CpuUsageTest
from diskspacetest import DiskspaceTest
from filecounttest import FileCountTest
from letsencryptrenewalstest import LetsEncryptRenewalsTest
from lxcuptimetest import LxcUptimeTest
from memorylxctest import MemoryLxcTest
from memorytest import MemoryTest
from needrestarttest import NeedRestartTest
from packageupgradetest import PackageUpgradeTest
from reportertest import ReporterTest
from servicemonitortest import ServiceMonitorTest
from senddatatest import SendDataTest
from simpleschedulertest import SimpleSchedulerTest
from threadpooltest import ThreadPoolTest
from uptimetest import UptimeTest
from urlstatustest import UrlStatusTest

if __name__ == '__main__':
    main()

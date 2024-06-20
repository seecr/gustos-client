## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2011-2014, 2018, 2021 Seecr (Seek You Too B.V.) https://seecr.nl
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

from seecr.test import SeecrTestCase, CallTrace
from seecr.test.io import stderr_replaced

from gustos.client.threadpool import ThreadPool
from time import sleep
from threading import active_count

class ThreadPoolTest(SeecrTestCase):
    def testPoolsize(self):
        with ThreadPool(verbose=False) as tp:
            self.assertEqual(0, len(tp._pools['used']))
            self.assertEqual(10, len(tp._pools['free']))
        with ThreadPool(size=20, verbose=False) as tp:
            self.assertEqual(0, len(tp._pools['used']))
            self.assertEqual(20, len(tp._pools['free']))

    def testThreadAreRunning(self):
        with ThreadPool(verbose=False) as tp:
            for thread in tp._pools['free']:
                self.assertTrue(thread.is_alive())
                self.assertTrue(thread.daemon)

    def testSemaphoreUsage(self):
        semaphore = CallTrace()
        with ThreadPool(semaphore=semaphore, verbose=False) as tp:
            processed = []
            def job():
                processed.append(True)
                self.assertEqual(1, len(tp._pools['used']))
                self.assertEqual(9, len(tp._pools['free']))
            tp.doJob(job)

            count = 0
            while len(processed) == 0  and count < 300:
                sleep(0.01)
                count += 1

            self.assertEqual([True], processed)
            self.assertEqual(['acquire', 'release', 'acquire', 'release'], semaphore.calledMethodNames())
            self.assertEqual(0, len(tp._pools['used']))
            self.assertEqual(10, len(tp._pools['free']))

    def testExceptionInJob(self):
        with stderr_replaced() as err:
            semaphore = CallTrace()
            with ThreadPool(semaphore=semaphore, verbose=False) as tp:

                processed = []
                def job():
                    processed.append(True)
                    raise Exception()
                tp.doJob(job)

                count = 0
                while len(processed) == 0  and count < 1000000:
                    sleep(0.01)
                    count += 1

                self.assertEqual(0, len(tp._pools['used']))
                self.assertEqual(10, len(tp._pools['free']))
            self.assertEqual('Traceback (most recent call last):', err.getvalue().split('\n')[0])
            self.assertEqual('Exception', err.getvalue().split('\n')[-2])

    def testStopThreads(self):
        with ThreadPool(verbose=False):
            self.assertEqual(11, active_count())
        sleep(0.05)
        self.assertEqual(1, active_count())

    def testNoFreeThreadsAvailable(self):
        t = ThreadPool(size=0, verbose=False)
        try:
            t.doJob(lambda: None)
        except ValueError as e:
            self.assertEqual('No free threads available. More than 0 concurrent jobs.', str(e))

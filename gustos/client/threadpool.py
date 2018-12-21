## begin license ##
#
# "Gustos" is a monitoring tool by Seecr. This client side code for connecting with Gustos server.
#
# Copyright (C) 2012-2014, 2018 Seecr (Seek You Too B.V.) https://seecr.nl
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

from threading import Thread as _Thread, Condition, Semaphore
from traceback import print_exc
from time import sleep
import sys

class ThreadPool(object):
    def __init__(self, size=10, semaphore=None, verbose=True):
        self._size = size
        self._verbose = verbose
        self._pools = dict(used=[], free=[])
        self._semaphore = Semaphore() if semaphore is None else semaphore
        for i in range(self._size):
            thread = Thread(pool=self, identifier=i)
            thread.setDaemon(True)
            thread.start()
            self._pools['free'].append(thread)
        sleep(0.0001)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def stop(self):
        for thread in self._pools['free']:
            thread.stop()
        for thread in self._pools['used']:
            thread.stop()

    def doJob(self, job):
        thread = self._getFreeThread()
        thread.doJob(job)

    def _getFreeThread(self):
        if not self._pools['free']:
            raise ValueError('No free threads available. More than %s concurrent jobs.' % self._size)
        self._semaphore.acquire()
        try:
            inuse = thread_identifiers(self._pools['used'])
            thread = self._pools['free'].pop()
            self._pools['used'].append(thread)
            self._log('Using thread #{:03d}, in use: {}'.format(thread.identifier, inuse))
            return thread
        finally:
            self._semaphore.release()

    def releaseThread(self, thread):
        self._semaphore.acquire()
        try:
            self._pools['used'].remove(thread)
            self._pools['free'].append(thread)
            inuse = thread_identifiers(self._pools['used'])
            self._log('Released thread #{:03d}, in use: {}'.format(thread.identifier, inuse))
        finally:
            self._semaphore.release()

    def _log(self, message):
        if not self._verbose:
            return
        sys.stdout.write("{0}\n".format(message))
        sys.stdout.flush()

thread_identifiers = lambda threads: ', '.join(str(t.identifier) for t in sorted(threads))

class Thread(_Thread):
    def __init__(self, pool, identifier, *args, **kwargs):
        _Thread.__init__(self, *args, **kwargs)
        self._condition = Condition()
        self._pool = pool
        self._job = None
        self._stop = False
        self.identifier = identifier

    def doJob(self, job):
        self._job = job
        self._condition.acquire()
        try:
            self._condition.notify()
        finally:
            self._condition.release()

    def stop(self):
        self._stop = True
        self._condition.acquire()
        try:
            self._condition.notify()
        finally:
            self._condition.release()

    def run(self):
        while True:
            self._condition.acquire()
            self._condition.wait()
            if self._stop:
                break
            try:
                try:
                    self._job()
                except Exception as e:
                    print_exc()
            finally:
                self._job = None
                self._condition.release()
                self._pool.releaseThread(self)

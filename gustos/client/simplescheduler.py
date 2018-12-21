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

from time import time, sleep

class SimpleScheduler(object):
    def __init__(self):
        self._schedule = PriorityQueue()

    def addTimer(self, seconds, callback):
        self._schedule.put((self._time() + seconds, callback))

    def loop(self):
        while True:
            self.step()

    def step(self):
        try:
            scheduledTask = self._schedule.get_nowait()
        except Empty:
            raise ValueError('No plugins available')
        if not scheduledTask:
            raise ValueError('Nothing left to do.')
        when, callback = scheduledTask
        waitTime = when - self._time()
        if waitTime > 0:
            self._sleep(waitTime)
        callback()

    def _time(self):
        return time()

    def _sleep(self, t):
        sleep(t)

from Queue import PriorityQueue, Empty

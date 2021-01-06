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

import sys
from os import makedirs, listdir
from os.path import join, isdir, isfile, abspath, splitext
from time import time, strftime, localtime
from traceback import print_exc, format_exc
from simplejson import dumps

from gustos.common import digest, print2
from .senders import UdpSender, TcpSender
from .reporter import ThreadedReporter, UnthreadedReporter
from .simplescheduler import SimpleScheduler

from .debug import listen                    #DO_NOT_DISTRIBUTE
listen()                                    #DO_NOT_DISTRIBUTE

class PluginModule(object):
    def __init__(self, load):
        self._loadGlobals = load
        self._globals = None

    def _mustReload(self):
        self._globals = None

    def __getattr__(self, attr):
        if self._globals is None:
            self._globals = self._loadGlobals()
        return self._globals[attr]

    def __setattr__(self, name, value):
        if name in ['_loadGlobals', '_globals']:
            return object.__setattr__(self, name, value)
        raise AttributeError("Set of an attribute is not allowed on a PluginModule")

class Client(object):
    def __init__(self, id, gustosHost, gustosPort, pluginDir=None, logpath=None, useTcp=False, reactor=None, threaded=True, threadPoolSize=10, verbose=False, sender=None):
        self._reactor = reactor or SimpleScheduler()
        self._id = id
        self._digest = digest(id)
        self._plugins = {}
        self._reporter = ThreadedReporter(threadPoolSize=threadPoolSize) if threaded else UnthreadedReporter()
        self._logpath = logpath
        self._verbose = verbose
        if sender is None:
            self.updateSender(host=gustosHost, port=gustosPort, useTcp=useTcp)
        else:
            self._sender = sender

        if not pluginDir is None:
            self._initializePlugins(abspath(pluginDir))

    def updateSender(self, host, port, useTcp=False):
        Sender = TcpSender if useTcp else UdpSender
        self._sender = Sender(host, port)

    def stop(self):
        self._reporter.stop()

    def _initializePlugins(self, pluginDir):
        plugins = sorted([
            (name, join(pluginDir, name) + ext) for (name,ext) in [splitext(f) for f in listdir(pluginDir) if isfile(join(pluginDir, f))] if ext == '.py'])

        for name, filePath in plugins:
            try:
                module = self._loadPluginModule(pluginName=name, filePath=filePath)
                pluginMeterKwargs = module.meter()
            except BaseException:
                exc_str = format_exc()
                print2("Error loading PluginModule: '%s' from file: '%s', original exception was:\n\n" % (name, filePath) + exc_str + '\n', file=sys.stderr, flush=True)
                raise RuntimeError('Plugin loading Failed')

            self.addMeter(**pluginMeterKwargs)

    def _loadPluginModule(self, pluginName, filePath):
        if pluginName in self._plugins:
            self._plugins[pluginName]._mustReload()
        else:
            def load():
                moduleGlobals = self._createGlobals(pluginName=pluginName, filePath=filePath)
                createdLocals = {}

                with open(filePath, "rb") as fp:
                    exec(compile(fp.read(), filePath, 'exec'), moduleGlobals, createdLocals)
                moduleGlobals.update(createdLocals)
                return moduleGlobals
            self._plugins[pluginName] = PluginModule(load)

        return self._plugins[pluginName]

    def _createGlobals(self, pluginName, filePath):
        result = {}
        result['__builtins__'] = globals()['__builtins__']
        result.update({
            '__name__': None,     # Both None, otherwise relative imports
            '__package__': None,  # are attempted.
            '__file__': filePath,
            '__doc__': """Dynamically imported plugin"""})
        return result

    def addMeter(self, meter, interval=5):
        meter.interval = interval
        targetTime = self._time() + interval
        self._schedule(targetTime, meter)
        self._log('Added meter {0} with interval {1}; Scheduled at {2}'.format(meter, interval, self._formattedTime(targetTime)))

    def start(self):
        self._reactor.loop()

    def _schedule(self, targetTime, meter):
        def callback():
            self._reporter.process(lambda: self._report(meter))
            newTargetTime = targetTime + meter.interval
            self._schedule(newTargetTime, meter)
            self._log('Scheduled meter {0} at {1}'.format(meter, self._formattedTime(newTargetTime)))
        waitTime = targetTime - self._time()
        if waitTime < 0:
            waitTime = 0
        self._reactor.addTimer(seconds=waitTime, callback=callback)

    def _report(self, meter):
        self._log("Processing meter {0}".format(meter))
        meterValues = None
        try:
            meterValues = meter.values()
        except Exception:
            print_exc()
            sys.stderr.flush()

        if meterValues is None:
            return

        if not type(meterValues) is list:
            meterValues = [meterValues]
        for values in meterValues:
            packet = self.report(values)
            if self._logpath:
                self._logData(meter, packet)

    def report(self, values):
        try:
            packet = {
                'sender': self._id,
                'digest': self._digest,
                'data': values,
                'timestamp': int(self._time() * 1000)
            }
            self._sender.send(dumps(packet))
            return packet
        except Exception:
            print_exc()
            sys.stderr.flush()

    def _logData(self, meter, packet):
        meterDirectory = join(self._logpath, meter.__class__.__name__)
        if not isdir(meterDirectory):
            makedirs(meterDirectory)
        dataFilename = join(meterDirectory, str(packet['timestamp']))
        while isfile(dataFilename):
            dataFilename += "#"

        with open(dataFilename, 'w') as fp:
            fp.write(dumps(packet))

    def _time(self):
        return time()

    def _formattedTime(self, time):
        return strftime("%Y-%m-%d %H:%M:%S", localtime(time))

    def _log(self, message):
        if not self._verbose:
            return
        sys.stdout.write("{0}: {1}\n".format(self._formattedTime(self._time()), message))
        sys.stdout.flush()

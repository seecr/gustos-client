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
from os import listdir, makedirs
from os.path import join, isdir
from shutil import rmtree
from io import StringIO
from time import time
from simplejson import loads

from seecr.test import CallTrace, SeecrTestCase
from seecr.test.io import stderr_replaced

from weightless.io import Reactor

from gustos.client import Client
from gustos.client.simplescheduler import SimpleScheduler
from gustos.client.senders import TcpSender, UdpSender
from gustos.common.units import EVENT


class ClientTest(SeecrTestCase):
    def setUp(self):
        SeecrTestCase.setUp(self)
        self.pluginDir = join(self.tempdir, 'plugins.d')
        makedirs(self.pluginDir)
        self.mockClock = MockClock()
        self.socket = MockSocket()
        self.client = Client(
            id="aServer",
            gustosHost="HOST",
            gustosPort="PORT",
            pluginDir=self.pluginDir,
            logpath=self.tempdir,
            threaded=False,
            sender=UdpSender(host="HOST", port="PORT", sok=self.socket))
        self.scheduler = self.client._reactor
        self.client._time = self.scheduler._time = self.mockClock.time
        self.sleeper = CallTrace('sleeper', methods={'sleep': self.mockClock.sleep})
        self.scheduler._sleep = self.sleeper.sleep

        class MyMeter(CallTrace):
            pass
        self.meter = MyMeter('some meter', returnValues=dict(values={'group': {'chartLabel': {'serieLabel': {'quantity': 42}}}}))

    def tearDown(self):
        whiteBucket = self.whiteBucket()
        if whiteBucket:
            del whiteBucket[:]
        SeecrTestCase.tearDown(self)

    def testSentPacket(self):
        self.mockClock.step()
        self.client._report(self.meter)
        self.assertEqual(['sendto', 'close'], self.socket.calledMethodNames())
        self.assertEqual(loads('{"data": {"group": {"chartLabel": {"serieLabel": {"quantity": 42}}}}, "sender": "aServer", "digest": "8eb546039ef7a6091702566856d304a0923bd74d", "timestamp": 1000}'), loads(self.socket.calledMethods[0].args[0]))
        self.assertEqual(('HOST', 'PORT'), self.socket.calledMethods[0].args[1])

    def testSentMultiplePackets(self):
        meter = CallTrace('some meter', returnValues=dict(values=[
                    {'group': {'chartLabel': {'serieLabel': {'quantity': 42}}}},
                    {'othergroup': {'chartLabel': {'serieLabel': {'quantity': 43}}}}
                ]
            ))
        self.mockClock.step()
        self.client._report(meter)
        self.assertEqual(['sendto', 'close', 'sendto', 'close'], self.socket.calledMethodNames())
        self.assertEqual(loads('{"data": {"group": {"chartLabel": {"serieLabel": {"quantity": 42}}}}, "sender": "aServer", "digest": "8eb546039ef7a6091702566856d304a0923bd74d", "timestamp": 1000}'), loads(self.socket.calledMethods[0].args[0]))
        self.assertEqual(('HOST', 'PORT'), self.socket.calledMethods[0].args[1])

        self.assertEqual(loads('{"data": {"othergroup": {"chartLabel": {"serieLabel": {"quantity": 43}}}}, "sender": "aServer", "digest": "8eb546039ef7a6091702566856d304a0923bd74d", "timestamp": 2000}'), loads(self.socket.calledMethods[2].args[0]))
        self.assertEqual(('HOST', 'PORT'), self.socket.calledMethods[2].args[1])


    def testDontReportEmptyValues(self):
        self.mockClock.step()
        meter = CallTrace(returnValues={'values': None})
        self.client._report(meter)
        self.assertEqual([], self.socket.calledMethodNames())

    def testScheduling(self):
        self.client.addMeter(self.meter, interval=5)
        self.assertEqual(
            [(6, self._nextCallback(self.scheduler))],
             self.scheduler._schedule.queue)
        self.scheduler.step()
        self.assertEqual(['sleep'], self.sleeper.calledMethodNames())
        self.assertEqual(3, self.sleeper.calledMethods[0].args[0])
        self.assertEqual(['values'], self.meter.calledMethodNames())
        self.assertEqual(
            [(11, self._nextCallback(self.scheduler))],
            self.scheduler._schedule.queue)

    def testExceptionHandling(self):
        self.meter.exceptions['values'] = Exception("Something bad happened")
        self.client.addMeter(self.meter, interval=5)
        self.assertEqual(['plugins.d'], listdir(self.tempdir))
        self.assertEqual(
            [(6, self._nextCallback(self.scheduler))],
            self.scheduler._schedule.queue)

        strm = StringIO()
        try:
            sys.stderr = strm
            self.scheduler.step()
        finally:
            sys.stderr = sys.__stderr__

        self.assertEqual(['plugins.d'], listdir(self.tempdir))
        lines = strm.getvalue().split('\n')
        self.assertEqual('Traceback (most recent call last):', lines[0])
        self.assertEqual('Exception: Something bad happened', lines[-2])
        self.assertEqual(
            [(11, self._nextCallback(self.scheduler))],
            self.scheduler._schedule.queue)

    def testClientPacketLogging(self):
        self.client.addMeter(self.meter, interval=5)
        self.assertFalse(isdir(join(self.tempdir, 'MyMeter')))
        self.scheduler.step()
        self.assertTrue(isdir(join(self.tempdir, 'MyMeter')))
        self.assertEqual(['7000'], listdir(join(self.tempdir, 'MyMeter')))
        self.scheduler.step()
        self.scheduler.step()
        self.assertEqual(set(['7000', '12000', '17000']), set(listdir(join(self.tempdir, 'MyMeter'))))

    def testShouldAbspathOrNonePluginDir(self):
        data = dict(pluginDir=[])
        class MockClient(Client):
            def _initializePlugins(this, pluginDir):
                data['pluginDir'].append(pluginDir)

        kwargs = Dict(id='ignored', gustosHost='ignored', gustosPort=9999, threaded=False)

        client = MockClient(**kwargs)

        self.assertEqual([], data['pluginDir'])

        client = MockClient(**kwargs.copyUpdate(pluginDir=self.pluginDir))
        self.assertEqual([self.tempdir + '/plugins.d'], data['pluginDir'])
        data['pluginDir'] = []

        client = MockClient(**kwargs.copyUpdate(pluginDir='/../../../..' + self.pluginDir))
        self.assertEqual([self.tempdir + '/plugins.d'], data['pluginDir'])

    def testShouldImportPyFilesFromPluginDir(self):
        self.setPlugins(plugins={'testingmeter.py': PLUGIN_CONTENT_OK_WHITEBOX})

        kwargs = Dict(id='ignored', gustosHost='ignored', gustosPort=9999, pluginDir=self.pluginDir, threaded=False)
        client = Client(**kwargs)

        expected = set(['testingmeter.py'])
        result = set(listdir(self.pluginDir))
        self.assertEqual(expected, result, result.symmetric_difference(expected))
        whiteBucket = self.whiteBucket()
        self.assertTrue('import_complete' in whiteBucket, whiteBucket)
        self.assertEqual(['testingmeter'], list(client._plugins.keys()))

    def testShouldRaiseErrorOnBadImportFromPluginDir(self):
        self.setPlugins(plugins={'testingmeter.py': PLUGIN_CONTENT_NO_METER_WHITEBOX})

        kwargs = Dict(id='ignored', gustosHost='ignored', gustosPort=9999, pluginDir=self.pluginDir, threaded=False)

        with stderr_replaced() as err:
            try:
                client = Client(**kwargs)
            except RuntimeError as e:
                self.assertEqual('Plugin loading Failed', str(e))
            else:
                self.fail('Should not happen')

            errStr = err.getvalue()
            self.assertTrue("Error loading PluginModule: 'testingmeter' from file:" in errStr, errStr)
            self.assertTrue(", original exception was:\n" in errStr, errStr)
            self.assertTrue("Traceback " in errStr, errStr)

        # execfile, no "normal"-import; therefore no .pyc's
        expected = set(['testingmeter.py'])
        result = set(listdir(self.pluginDir))
        self.assertEqual(expected, result)
        whiteBucket = self.whiteBucket()

        # Ergo, import was ok, but "meter" global not present
        self.assertEqual(['start NO_METER_WHITEBOX', 'import_complete'], whiteBucket)

        self.setPlugins(plugins={'zarro.py': PLUGIN_CONTENT_WITH_ERROR_WHITEBOX})
        whiteBucket[:] = ['SENTINEL']
        with stderr_replaced() as err:
            try:
                Client(**kwargs)
            except RuntimeError as e:
                self.assertEqual('Plugin loading Failed', str(e))
            else:
                self.fail('Should not happen')

        # Error at import time
        self.assertEqual(['SENTINEL', 'start ERROR_WHITEBOX'], whiteBucket)

    def testShouldCallMeterFromImportedPlugins(self):
        self.setPlugins(plugins={
            'testingmeter.py': PLUGIN_CONTENT_OK_WHITEBOX,
            'p1*&#~`%+=.py': PLUGIN2_CONTENT_OK_WHITEBOX})

        mockClock = MockClock()
        sleeper = CallTrace('sleeper', methods={'sleep': mockClock.sleep})
        try:
            # save
            Client_time = Client._time
            _SimpleScheduler_time = SimpleScheduler._time
            _SimpleScheduler_sleep = SimpleScheduler._sleep

            # clz poke
            SimpleScheduler._sleep = lambda slf, t: sleeper.sleep(t)
            Client._time = lambda slf: mockClock.time()
            SimpleScheduler._time = lambda slf: mockClock.time()

            # Client(), read plugins and instance poke
            sender = UdpSender(host="HOST", port="PORT", sok=self.socket)
            client = Client(id="aServer", gustosHost="HOST", gustosPort="PORT", pluginDir=self.pluginDir, logpath=self.tempdir, threaded=False, sender=sender)
            scheduler = client._reactor

            # meter().values() not yet called
            self.assertEqual(['start OK_WHITEBOX plugin2', 'import_complete plugin2', 'start OK_WHITEBOX', 'import_complete'], self.whiteBucket())

            scheduler.step()
            scheduler.step()
        finally:
            Client._time = Client_time
            SimpleScheduler._time = _SimpleScheduler_time
            SimpleScheduler._sleep = _SimpleScheduler_sleep

        # meter().values() called
        self.assertEqual(['start OK_WHITEBOX plugin2', 'import_complete plugin2', 'start OK_WHITEBOX', 'import_complete'] + ['values_called_plugin2', 'values_called'], self.whiteBucket())

    def testShouldIgnoreNonFilesAndNonDotPyEndingNames(self):
        self.setPlugins(plugins={
            'testingmeter.otherext': PLUGIN_CONTENT_OK_WHITEBOX,
            'file.py.txt': PLUGIN_CONTENT_OK_WHITEBOX,
            'file_no_extension': PLUGIN_CONTENT_OK_WHITEBOX})

        kwargs = Dict(id='ignored', gustosHost='ignored', gustosPort=9999, pluginDir=self.pluginDir, threaded=False)
        client = Client(**kwargs)

        whiteBucket = self.whiteBucket()
        self.assertEqual([], whiteBucket)

    def testShouldHandleOddNames(self):
        self.setPlugins(plugins={'p1*&#~`%+=.py': PLUGIN_CONTENT_OK_WHITEBOX})

        kwargs = Dict(id='ignored', gustosHost='ignored', gustosPort=9999, pluginDir=self.pluginDir, threaded=False)
        client = Client(**kwargs)

        whiteBucket = self.whiteBucket()
        self.assertEqual(['start OK_WHITEBOX', 'import_complete'], whiteBucket)

    def testSchedulingWithWeightlessReactor(self):
        with Reactor() as reactor:
            sender = UdpSender(host='HOST', port='PORT', sok=self.socket)
            client = Client(reactor=reactor,
                id="aServer",
                gustosHost="HOST", gustosPort="PORT",
                logpath=self.tempdir, threaded=False,
                sender=sender)
            t0 = time()
            meter2 = CallTrace('another meter', returnValues=dict(
                values={'group2': {'chartLabel': {'serieLabel': {'quantity': 42}}}}))
            client.addMeter(self.meter, interval=0.09)
            client.addMeter(meter2, interval=0.19)
            self.assertEqual([], self.socket.calledMethodNames())
            reactor.step()
            self.assertEqual(['sendto', 'close'], self.socket.calledMethodNames())
            reactor.step()
            reactor.step()
            reactor.step()
            reactor.step()
        deltaT = time() - t0

        self.assertEqual(
            ['group', 'group', 'group2', 'group', 'group'],
            [
                ''.join(list(loads(m.args[0])['data'].keys()))
                for m in self.socket.calledMethods if m.name != "close"
            ]
        )
        self.assertTrue(0.36 < deltaT < 0.38, deltaT)

    def testSchedulingDoesntExceedRecursionDepth(self):
        self.client.addMeter(self.meter, interval=0.1)
        numberOfReports = sys.getrecursionlimit() + 1
        for i in range(numberOfReports):
            self.scheduler.step()
        self.assertEqual(numberOfReports * ['sendto', 'close'], self.socket.calledMethodNames())

    def testClientWithoutReactor(self):
        sender = UdpSender(host='HOST', port='PORT', sok=self.socket)
        client = Client(id="aServer", gustosHost="HOST", gustosPort="PORT", logpath=self.tempdir, threaded=False, sender=sender)
        client._time = lambda: 1

        client.report({"Queries": {"API-1": { "queries": { EVENT: 10 }}}})

        self.assertEqual(['sendto', 'close'], self.socket.calledMethodNames())
        data, remote = self.socket.calledMethods[0].args
        self.assertEqual(('HOST', 'PORT'), remote)
        self.assertEqual({"timestamp": 1000, "data": {"Queries": {"API-1": {"queries": {"event": 10}}}}, "sender": "aServer", "digest": "8eb546039ef7a6091702566856d304a0923bd74d"}, loads(data))

    def testUpdateConfig(self):
        client = Client(id="aServer", gustosHost="HOST", gustosPort="PORT", logpath=self.tempdir, threaded=False)
        self.assertEqual("HOST", client._sender._host)
        self.assertEqual("PORT", client._sender._port)
        self.assertEqual(UdpSender, type(client._sender))

        client.updateSender(useTcp=True, host="NEW_HOST", port="NEW_PORT")
        self.assertEqual("NEW_HOST", client._sender._host)
        self.assertEqual("NEW_PORT", client._sender._port)
        self.assertEqual(TcpSender, type(client._sender))

        client.updateSender(useTcp=False, host="NEW_HOST2", port="NEW_PORT2")
        self.assertEqual("NEW_HOST2", client._sender._host)
        self.assertEqual("NEW_PORT2", client._sender._port)
        self.assertEqual(UdpSender, type(client._sender))

    def testClientStop(self):
        mockReporter = CallTrace()
        client = Client(id="aServer", gustosHost="HOST", gustosPort="PORT", logpath=self.tempdir, threaded=False)
        client._reporter = mockReporter

        client.stop()
        self.assertEqual(["stop"], mockReporter.calledMethodNames())


    def setPlugins(self, plugins):
        if isdir(self.pluginDir):
            rmtree(self.pluginDir)
        makedirs(self.pluginDir)
        for fileName, content in plugins.items():
            with open(join(self.pluginDir, fileName), 'w') as f:
                f.write(content)

    def whiteBucket(self):
        if hasattr(sys.modules['gustos.common'], '_test_whiteboxing'):
            return sys.modules['gustos.common']._test_whiteboxing
        return None

    def _nextCallback(self, scheduler):
        return scheduler._schedule.queue[0][1]


class MockClock(object):
    def __init__(self):
        self.now = 0
        def times():
            while True:
                yield self.now
                self.now += 1
        self._timeGenerator = times()

    def time(self):
        self.step()
        return self.now

    def step(self):
        next(self._timeGenerator)

    def sleep(self, t):
        target = self.now + t
        while self.now != target:
            self.step()

class MockSocket(CallTrace):
    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        pass


class Dict(dict):

    def clear(self, *args, **kwargs):
        dict.clear(self, *args, **kwargs)
        return self

    def update(self, *args, **kwargs):
        dict.update(self, *args, **kwargs)
        return self

    def copyUpdate(self, *args, **kwargs):
        newDict = self.copy()
        newDict.update(*args, **kwargs)
        return newDict

PLUGIN_CONTENT_OK_WHITEBOX = """\
from gustos.common.units import PERCENTAGE
from gustos import common as gustosCommonModuleForTesting

if not hasattr(gustosCommonModuleForTesting, '_test_whiteboxing'):
    gustosCommonModuleForTesting._test_whiteboxing = []
_test_whiteboxing = gustosCommonModuleForTesting._test_whiteboxing
_test_whiteboxing.append('start OK_WHITEBOX')

class SomeMeter(object):
    def values(self):
        _test_whiteboxing.append('values_called')
        return {
            'TestingGroup': {
                'ChartLabel': {
                    'lineLabel': {
                        PERCENTAGE: 10.0
                    }
                }
            }
        }

def meter():
    return dict(meter=SomeMeter(), interval=1)

_test_whiteboxing.append('import_complete')
"""

PLUGIN2_CONTENT_OK_WHITEBOX = """\
from gustos.common.units import PERCENTAGE
from gustos import common as gustosCommonModuleForTesting

if not hasattr(gustosCommonModuleForTesting, '_test_whiteboxing'):
    gustosCommonModuleForTesting._test_whiteboxing = []
_test_whiteboxing = gustosCommonModuleForTesting._test_whiteboxing
_test_whiteboxing.append('start OK_WHITEBOX plugin2')

class SomeMeter(object):
    def values(self):
        _test_whiteboxing.append('values_called_plugin2')
        return {
            'TestingGroup': {
                'ChartLabel': {
                    'lineLabel': {
                        PERCENTAGE: 10.0
                    }
                }
            }
        }

def meter():
    return dict(meter=SomeMeter(), interval=1)

_test_whiteboxing.append('import_complete plugin2')
"""

PLUGIN_CONTENT_NO_METER_WHITEBOX = """\
from gustos import common as gustosCommonModuleForTesting

if not hasattr(gustosCommonModuleForTesting, '_test_whiteboxing'):
    gustosCommonModuleForTesting._test_whiteboxing = []
_test_whiteboxing = gustosCommonModuleForTesting._test_whiteboxing
_test_whiteboxing.append('start NO_METER_WHITEBOX')

_test_whiteboxing.append('import_complete')
"""

PLUGIN_CONTENT_WITH_ERROR_WHITEBOX = """\
from gustos import common as gustosCommonModuleForTesting

if not hasattr(gustosCommonModuleForTesting, '_test_whiteboxing'):
    gustosCommonModuleForTesting._test_whiteboxing = []
_test_whiteboxing = gustosCommonModuleForTesting._test_whiteboxing
_test_whiteboxing.append('start ERROR_WHITEBOX')

zeroDivisionError = 1 / 0

_test_whiteboxing.append('import_complete')
"""

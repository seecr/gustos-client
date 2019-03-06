## begin license ##
#
# All rights reserved.
#
# Copyright (C) 2014 Seecr (Seek You Too B.V.) http://seecr.nl
#
## end license ##

from os.path import splitext, realpath
from simplejson import load
from gustos.client.servicemonitor import ServiceMonitor

def meter():
    jsonConfig = splitext(realpath(__file__))[0] + ".json"
    arguments = load(open(jsonConfig))
    return dict(meter=ServiceMonitor(**arguments), interval=60)

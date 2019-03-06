## begin license ##
#
# All rights reserved.
#
# Copyright (C) 2013-2014 Seecr (Seek You Too B.V.) http://seecr.nl
#
## end license ##

from gustos.client.securityupdates import SecurityUpdates

def meter():
    return dict(meter=SecurityUpdates(), interval=600)


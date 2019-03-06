## begin license ##
#
# All rights reserved.
#
# Copyright (C) 2013-2014 Seecr (Seek You Too B.V.) http://seecr.nl
#
## end license ##

from gustos.client import NeedRestart

def meter():
    return dict(meter=NeedRestart(
        ignore=["svscanboot", "svscan", "run", "supervise", "multilog", "readproctitle", "lxc-start", "seecr-daemontoo", "agetty"]), 
        interval=1*60*60)


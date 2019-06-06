# A class to hold the assorted information about what a particular page contains that we can glean from scanning the website.
import Helpers
import os
import os.path
from dataclasses import dataclass, field


@dataclass(order=False)
class FanacInformation(object):
    _Displayname: str=None    # Text for the page's display name

    def __init__(self, Displayname=None):
        self._Displayname=Displayname

    @property
    def Displayname(self):
        return self._Displayname


import Helpers

# A file to define the Reference class
from dataclasses import dataclass, field

@dataclass(order=False)
class FFReference(object):
    CanonName: str=None     # The Wikidot canonical name
    Name: str=None          # The display name
    _FancyRefs: list=None    # A list of canonical names of referring pages from Fancy
    _FanacRefs: list=None    # A list of relative paths of referring Fanac files

    def __init__(self, CanonName=None, Name=None, FancyRefs=None, FanacRefs=None):
        self.Name=Name
        self.CanonName=CanonName
        if Name is not None and CanonName is None:
            self.CanonName=Helpers.CanonicizeString(Name)
        self._FancyRefs=FancyRefs
        self._FanacRefs=FanacRefs

    @property
    def FancyRefs(self):
        return self._FancyRefs

    @FancyRefs.setter
    def FancyRefs(self, value):
        print("setter of FancyRefs for "+self.Name+" called")
        self._FancyRefs = value

    def AppendFancyRef(self, value):
        if self._FancyRefs is None:
            self._FancyRefs=[]
        print("append to FancyRefs for "+self.Name)
        self._FancyRefs.append(value)

    @property
    def FanacRefs(self):
        return self._FanacRefs

    @FanacRefs.setter
    def FanacRefs(self, value):
        print("setter of FanacRefs for "+self.Name+" called")
        self._FanacRefs = value

    def AppendFanacRef(self, value):
        if self._FanacRefs is None:
            self._FanacRefs=[]
        print("append to FanacRefs for "+self.Name)
        self._FanacRefs.append(value)
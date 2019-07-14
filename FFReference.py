# A file to define the Reference class
import Helpers
import os
import os.path
from dataclasses import dataclass, field
import FanacIssuePages
from FanacIssuePages import FanacIssuePages


@dataclass(order=False)
class FFReference(object):
    CanonName: str     # The Wikidot canonical name
    Name: str          # The display name
    _FancyRefs: list    # A list of strings: canonical names of referring pages from Fancy
    _FanacRefs: list    # A list of FanacIssuePages objects

    def __init__(self, CanonName=None, Name=None, FanacStr=None):
        self.Name=Name
        self.CanonName=None
        self._FancyRefs=None
        self._FanacRefs=None

        if CanonName is not None:
            self.CanonName=CanonName

        if Name is not None:
            self.Name=Name
            if CanonName is None:
                self.CanonName=Helpers.CanonicizeString(Name)

        if FanacStr is not None:
            fi=FanacIssuePages()
            fi.InitFromString(FanacStr)
            self._FanacRefs=[fi]

    @property
    def NumFancyRefs(self):
        if self.FancyRefs is None:
            return 0
        return len(self.FancyRefs)

    @property
    def FancyRefs(self):
        return self._FancyRefs

    @FancyRefs.setter
    def FancyRefs(self, value):
        self._FancyRefs = value

    def AppendFancyRef(self, value):
        if self._FancyRefs is None:
            self._FancyRefs=[]
        self._FancyRefs.append(value)

    @property
    def FanacRefs(self):
        return self._FanacRefs

    @property
    def FanacRefsString(self):
        out=""
        for fi in self._FanacRefs:
            if len(out) > 0:
                out+=", "
            out=out+fi.Format()
        return out

    @FanacRefs.setter
    def FanacRefs(self, value):
        self._FanacRefs=value

    @property
    def NumFanacRefs(self):
        if self.FanacRefs is None:
            return 0
        return len(self.FanacRefs)

    #**********************
    # Append a Fanac reference.  This may be just a string or this may be convertible to a FanacIssue
    def AppendFanacRef(self, fip: FanacIssuePages):
        if self._FanacRefs is None or len(self._FanacRefs) == 0:
            self._FanacRefs=[fip]
            return

        # Can this be merged with the last FanacIssue?
        lastFIP=self._FanacRefs[-1:][0]
        if lastFIP.Merge(fip):
            return

        # Nope. Just append it to the list
        self._FanacRefs.append(fip)


    #**********************
    # Add two FFRs together
    def __add__(self, other):
        if self.Name is None:
            self.Name=other.Name
            self.CanonName=other.CanonName

        if self._FanacRefs is None:
            self._FanacRefs=other._FanacRefs
        elif other._FanacRefs is not None:
            self._FanacRefs.extend(other._FanacRefs)

        if self._FancyRefs is None:
            self._FancyRefs=other._FancyRefs
        elif other._FancyRefs is not None:
            self._FancyRefs.extend(other._FancyRefs)

    #**********************
    def Merge(self, other):
        if self.Name != other.name:
            return False

        if other._FancyRefs is not None:
            if self._FancyRefs is None:
                self._FancyRefs=other._FancyRefs
            else:
                self._FancyRefs.extend(other._FancyRefs)

        if other._FanacRefs is not None:
            if self._FanacRefs is None:
                self._FanacRefs=other._FanacRefs
            else:
                self._FanacRefs.extend(other._FanacRefs)


    #**********************
    def SortFancyRefs(self):
        if self._FancyRefs is not None and len(self._FancyRefs) > 0:
            self._FancyRefs.sort()

    #**********************
    def SortFanacRefs(self):
        if self._FanacRefs is not None and len(self._FanacRefs) > 0:
            self._FanacRefs.sort(key=lambda x: x.SortName)

# A class to define the a list of pages in an issue of a publication
import Helpers
import os
import os.path
from dataclasses import dataclass, field


@dataclass(order=False)
class FanacIssue(object):
    _Pathname: str=None     # Full path and filename (relative to public) of the first issue in the list
    _PageList: list=None    # List of strings making up the pagelist
    _DisplayName: str=None  # The visible name to be used for this issue

    def __init__(self, Pathname=None, Issuelist=None, Str=None):
        if Str == None:
            self._Pathname=Pathname
            self._PageList=Issuelist
        else:
            self.Append(Str)

    def __lt__(self, second):
        if isinstance(second, FanacIssue):
            return self._Pathname < second._Pathname
        return self._Pathname < second

    def InitFromString(self, s: str):
        name, page=IsFanacIssuePage(s)
        if name is None:
            name=s
        self._Pathname=name
        self._PageList=[page]

    @property
    def PageList(self):
        return self._PageList

    @property
    def Pathname(self):
        return self._Pathname

    @property
    def SortName(self):
        if self._Pathname is not None:
            return self._Pathname
        return " "


    #******************************
    # Append a reference string to this class instance
    def Append(self, s: str):
        name, page=IsFanacIssuePage(s)

        # Is this a new, empty instance?
        if self._Pathname == None and self._PageList == None:
            self._Pathname=name
            if page is not None:
                self._PageList=[page]
            return True

        # OK, we're (maybe) appending to an existing instance
        if page is None:
            self._Pathname=s
            return False
        if name != self._Pathname:
            return False
        self._PageList.append(page)


    #******************************
    # Format the FI for printing
    def Format(self, Displayname=None):
        issueName=self._Pathname
        if Displayname is not None:
            issueName=Displayname
        if issueName is None or len(issueName) == 0:  # This is likely an error
            return "FanacIssue.Format of None"

        if self._PageList == None or len(self._PageList) == 0:    # There's a filename, but no page number
            return issueName
        self.DeDup()
        pages=[p.lstrip("0") for p in self._PageList]
        pages=[p if p != "" else "0" for p in pages]
        if len(pages) > 1:
            return issueName+" pp "+",".join(pages)
        elif len(pages) == 1:
            return issueName+" p"+pages[0]
        return issueName

    #******************************
    # Merge two fanac page references
    # They can be merged if they are both of the form:
    #   <path><name>-##.html
    # The second (numbered $$) would be merged into the first to form where ## was the lower of the numbers
    # Additionally, ##,$$ (etc) would be in ascending order and runs 2,3,4 would be written 2-4.
    #   <path><name>--##.html (##,$$)
    # This does not modify either page reference, but returns a new one representing both
    def Merge(self, other):
        if self._Pathname != other._Pathname:
            return False

        if other._PageList is None:
            return True

        if self._PageList is None:
            self._PageList=other._PageList
            return True

        self._PageList.extend(other._PageList)
        return True


    #******************************
    # Remove duplicate entries from the pagelist
    def DeDup(self):
        if self._PageList is None or len(self._PageList) == 0:
            return
        self.SortPagelist()
        i=0
        while i < len(self._PageList)-1:
            if self._PageList[i] == self._PageList[i+1]:
                self._PageList[i]=None
            i=i+1
        self._PageList=[p for p in self._PageList if p is not None]


    #******************************
    # Sort a pagelist
    def SortPagelist(self):
        if self._PageList is not None:
            self._PageList.sort(key=lambda n: numsSortKey(n))


#******************************************************************
def jacksNumbers(s: str):
    s=s.lower()
    if s == "cv" or s == "fc": return -10
    if s == "ic" or s == "if" or s == "ifc": return -9
    if s == "tc" or s == "con": return -3
    if s == "cf": return 500
    if s == "bc": return 900
    if s == "er": return 550
    if s == "ib" or s == "ibc": return 899
    if s == "ins": return 600
    if s == "r1": return -8
    if s == "r2": return -7
    if s == "r3": return -6
    if s == "r4": return -5
    if s == "r5": return -4
    if s == "i1": return 601
    if s == "i2": return 602
    if s == "i3": return 603
    if s == "i4": return 604
    if s == "i5": return 605
    try:
        return int(s)
    except:
        pass
    return None


#******************************************************************
def numsSortKey(n: str):
    if n is None or len(n) == 0:  # Put blank or missing at front.
        return -99

    val=jacksNumbers(n)
    if val is not None:
        return val
    # Maybe it's a range. If so, return the start of the range
    ns=n.split("-")
    if len(ns) == 2:
        val=jacksNumbers(ns[0])
        if val is not None:
            return val
    return 999  # Uninterpretable. Put it at the end.


#******************************************************************
# Is this string a properly formatted Fanac issue page relative path?
# If so, return the issue spec and the page spec as separate string
# If not, return None, None
def IsFanacIssuePage(s: str):
    f, e=os.path.splitext(s)  # Is the extension HTML?
    if e.lower() != ".html":
        return None, None

    p, f=os.path.split(f)
    parts=f.split("-")  # Is there a hyphen in the filename?
    if len(parts) != 2:
        return None, None

    if jacksNumbers(parts[1]) is None:  # Is the bit following the hyphen a Fanac-standard page number?
        return None, None

    return os.path.join(p, parts[0]), parts[1]


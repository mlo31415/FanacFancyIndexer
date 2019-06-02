# A file to define the Reference class
import Helpers
import os
import os.path
from dataclasses import dataclass, field


@dataclass(order=False)
class FanacIssue(object):
    _Pathname: str=None     # Full path and filename (relative to public) of the first issue in the list
    _Issuelist: list=None   # List of strings making up the pagelist

    def __init__(self, Pathname=None, Issuelist=None, Str=None):
        if Str == None:
            self._Pathname=Pathname
            self._Issuelist=Issuelist
        else:
            self.Append(Str)

    def __lt__(self, second):
        if isinstance(second, FanacIssue):
            return self._Pathname < second._Pathname
        return self._Pathname < second

    def InitFromString(self, s: str):
        page, issue=IsFanacIssuePage(s)
        if issue is None:
            page=s
        self._Pathname=page
        self._Issuelist=[issue]

    @property
    def Issuelist(self):
        return self._Issuelist

    @property
    def Pathname(self):
        return self._Pathname

    @property
    def SortName(self):
        if self._Pathname is not None:
            return self._Pathname
        return " "

    # Append a reference string to this class instance
    def Append(self, s: str):
        page, issue=IsFanacIssuePage(s)
        if issue is None:
            self._Pathname=s
            return False
        if page != self._Pathname:
            return False
        self._Issuelist.append(issue)

    # Format the FI for printing
    def Format(self):
        if self._Pathname is None or len(self._Pathname) == 0:
            return "Attempt to format null FanacIssue"
        if self._Issuelist == None or len(self._Issuelist) == 0:
            return self._Pathname
        temp=[i if i is not None else "None" for i in self._Issuelist]  #TODO: remove this when we're properly handling None issues
        return self._Pathname+" ("+",".join(temp)+")"


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

        if other._Issuelist is None:
            return True

        if self._Issuelist is None:
            self._Issuelist=other._Issuelist
            return True

        self._Issuelist.extend(other._Issuelist)
        self._Issuelist.sort(key=lambda n: numsSortKey(n))
        return True


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


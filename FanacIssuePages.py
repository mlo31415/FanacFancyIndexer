# A class to define the a list of pages in a single issue of a publication
import Helpers
import os
import os.path
from dataclasses import dataclass, field


@dataclass(order=False)
class FanacIssuePages(object):
    _Path: str=None             # The path relative to public of the issue
    _FirstPageName: str=None    # The name of the first page of the issue
    _PageList: list=None        # List of tuples (strings making up the page numbers, page file name)  E.g., (5, fanz017-05.html)
    _DisplayName: str=None      # The visible name to be used for this issue

    def __init__(self, Path=None, FirstPageName=None, PageList=None, DisplayName=None, PageName=None):
        if self._Path is None:
            self._Path=Path
        if self._FirstPageName is None:
            self._FirstPageName=FirstPageName
        if self._PageList is None:
            self._PageList=PageList
        if self._DisplayName is None:
            self._DisplayName=DisplayName

        if PageName is not None:
            self.InitFromString(PageName)

    # def __lt__(self, second):
    #     if isinstance(second, FanacIssuePages):
    #         return self._Path < second._Path
    #     return self._Pathn < second

    def InitFromString(self, s: str):
        path, pagename=IsFanacIssuePage(s)
        if path is None:
            pagename=s
        if path is not None:
            self._Path=path
        self._PageList=[("-1", pagename)]

    @property
    def PageList(self):
        return self._PageList

    @property
    def Path(self):
        return self._Path

    @property
    def SortName(self):
        p=""
        f=""
        if self._Path is not None:
            p=self._Path
        if self._FirstPageName is not None:
            f=self._FirstPageName

        return p+"/"+f


    #******************************
    # Append a reference string to this class instance
    def Append(self, s: str):
        name, page=IsFanacIssuePage(s)

        # Is this a new, empty instance?
        if self._Path == None and self._PageList == None:
            self._Path=name
            if page is not None:
                self._PageList=[page]
            return True

        # OK, we're (maybe) appending to an existing instance
        if page is None:
            self._Path=s
            return False
        if name != self._Path:
            return False
        self._PageList.append(page)


    #******************************
    # Format the FI for printing
    def Format(self, Displayname=None):
        issueName=self._Path
        if Displayname is not None:
            issueName=Displayname
        if issueName is None or len(issueName) == 0:  # This is likely an error
            return "FanacIssue.Format of None"

        if self._PageList == None or len(self._PageList) == 0:    # There's a filename, but no page number
            return issueName
        self.DeDup()
        pages=[p[0].lstrip("0") for p in self._PageList]
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
        if self._Path != other._Path:
            return False

        if other._PageList is None:
            return True     # Nothing to merge, so it's done

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
            self._PageList.sort(key=lambda n: numsSortKey(n[0]))


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


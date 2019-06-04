#------------------------------------------------------------------
# Take an arbitrary string and return it in Wikidot Canonical form
def CanonicizeString(name: str):
    out = []
    inJunk = False
    name=name.lower()
    for c in name:
        if c.isalnum() or c == ':':     # ":", the category separator, is an honorary alphanumeric
            if inJunk:
                out.append("-")
            out.append(c)
            inJunk = False
        else:
            inJunk = True
    # Remove any leading or trailing "-"
    canName=''.join(out)
    if len(canName) > 1:
        if canName[0] == "-":
            canName=canName[1:]
        if canName[:-1] == "-":
            canName=canName[:-1]
    return canName


#------------------------------------------------------------------
# Split a really long string of output for printing as text.
def splitOutput(f, s: str):
    strs=s.split(",")
    while len(strs) > 0:
        out=""
        while (len(strs) > 0 and (len(out)+len(strs[0])) < 80 or (len(out) == 0 and len(strs[0]) >= 80)):
            out=out+strs[0].strip()+", "
            del strs[0]
        f.write("    "+out+"\n")



#------------------------------------------------------------------
# Decode the Fanac path relative to /public/ to determine what category this reference is
def fanacCategory(s: str):
    if s.find("Fan_Photo_Album") > -1:
        return "Photo"
    if s.startswith(r"\fanzines"):
        return "Fanzine"
    if s.startswith(r"\fan_funds"):
        return "Fanzine"
    if s.startswith(r"\Fan_Histories"):
        return "Fanzine"
    if s.startswith(r"\Fannish_Reference_Works"):
        return "Fanzine"
    if s.find("Photo") > -1:
        return "Photo"

    return "Unknown"


#------------------------------------------------------------------
# Given the Fanac path relative to /public/, determine a good display title
def fanacDisplayName(s: str):
    return s
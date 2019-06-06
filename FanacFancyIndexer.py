import os
import os.path
import FFReference
import FanacInformation
import Helpers

# Read the Fancy redirection data.  This will create a dictionar which allows us to turn variant names into standard forms.
fancyDataPath=r"..\FancyNameExtractor"
# Read the Fancy canonical names data
with open(os.path.join(fancyDataPath, "Redirects.txt"), "rb") as f:
    fancyRedirectsText=f.read().decode("cp437").splitlines()

# Build a redirection table
# The input is a file with lines beginning with "**"" which are page names
# They are followed by pages beginning "  " which are canonical name sof pages which redirect to them
# Build a dictionary of canonical page names and the page they redirect to.
redirectionTargets={}
target=""
for line in fancyRedirectsText:
    if len(line) <3:
        continue    # Shouldn't happen, really.
    if line[:2] == "**":
        target=line[2:]
    elif line[:2] == "  ":
        redirectionTargets[line[2:]]=target
    else:
        assert(False)   # Should never happen


references={}   # This will be a dictionary indexed by display name with the value being an FFReference structure

# Read the Fanac data
# In consists of lines of text containing a name separted by a "|" from a path relative to public to the file the reference comes from.
fanacDataPath=r"..\FanacNameExtractor"
with open(os.path.join(fanacDataPath, "Fanac name path pairs.txt"), "r") as f:
    fanacReferencesText=f.read().splitlines()

# Create a dictionary of names with the value being a FFReference
for line in fanacReferencesText:
    parts=line.split("|")
    parts=[p.strip() for p in parts]    # Split into name + reference
    try:
        ref=references[parts[0]]
    except:
        references[parts[0]]=FFReference.FFReference(Name=parts[0])
    references[parts[0]].AppendFanacRef(parts[1])

print("Fanac yielded "+str(len(references))+" distinct names")

# Now read the Fancy data
# It consists of a line starting "**" containing the referred-to name
# Those are followed by one or more lines beginning "  " containing the canonical name of a referring page
fancyDataPath=r"..\FancyNameExtractor"
with open(os.path.join(fancyDataPath, "Referring pages.txt"), "r") as f:
    fancyReferencesText=f.read().splitlines()

ffr=None
count=0
for line in fancyReferencesText:
    if line.startswith("**"):
        name=line[2:]
        if name in references.keys():
            ffr=references[name]
            count+=1
        else:
            ffr=FFReference.FFReference(Name=name)
            references[name]=ffr
        continue
    ffr.AppendFancyRef(line.strip())
print("Fancy yielded "+str(count)+" distinct names")
print("For a total of "+str(len(references)))

# Create the canonical to real names dictionary
canonNameToFull={}
with open(os.path.join(fancyDataPath, "Canonical names to real names.txt"), "rb") as f:
    canonToTitleText=f.read().decode("utf-8").splitlines()
for line in canonToTitleText:
    canon, title=line.split("-->")
    canonNameToFull[canon]=title


# Now combine multiple versions of the same name
# We can't delete the duplicate FFRs without messing up the iteration, so we justs ent their value to None and remove them afterwards
for name in references:
    ffr=references[name]
    if ffr.CanonName in redirectionTargets.keys():
        # This canonical name is redirected elsewhere.
        redirect=redirectionTargets[ffr.CanonName]
        if redirect in references.keys():
            targetFFR=references[redirect]
            if targetFFR is not None:
                targetFFR+=ffr
            else:
                targetFFR=ffr
            references[name]=None

# That targeted dictionary entries for removal by setting the value to None. So remove them from the dictionary
newrefs={}
for k, v in references.items():
    if v is not None:
        newrefs[k]=v
references=newrefs

print("Combining synonyms brought it to "+str(len(references))+" distinct names")

# Read in the list of people from fancy
with open(os.path.join(fancyDataPath, "Peoples names.txt"), "rb") as f:
    peoplePagesFancy=f.read().decode("cp437").splitlines()

# Sort the Fancy and Fanac referring pages lists for each person
for key, ref in references.items():
    ref.SortFanacRefs()
    ref.SortFancyRefs()

# Merge references to different pages of the same issue in Fanac
# The strategy is to take #1 and compare it with #2.  If those merge, try #3 into #1. When it eventually fails, go to the failure and try to merge the one after than into it.  Etc.
for key, ref in references.items():
    if ref.FanacRefs is None or len(ref.FanacRefs) == 0:
        continue

    for ffr in ref.FanacRefs:
        ffr.SortPagelist()
    refs=ref.FanacRefs
    indexBase=0
    indexMerge=1

    while indexMerge < len(refs):
        refBase=refs[indexBase]
        if refBase is None:
            indexBase+=1
            indexMerge=indexBase+1
            continue

        refMerge=refs[indexMerge]
        if refMerge is None:
            indexMerge+=1
            continue

        if not refBase.Merge(refMerge):
            indexBase=indexMerge
            indexMerge=indexBase+1
            continue

        refs[indexMerge]=None
        indexMerge+=1

    # Get rid of any deleted refs
    ref.FanacRefs=[r for r in refs if r is not None]

# Load the table of URL information that was generated by FanacNameExtractor
with open(os.path.join(fanacDataPath, "Fanac information.txt"), "rb") as f:
    fanacInformationText=f.read().decode("utf-8").splitlines()

fanacInformation={}
for line in fanacInformationText:
    line=[li.strip() for li in line.split("|")]
    fanacInformation[line[0]]=FanacInformation.FanacInformation(Displayname=line[1])


# Generate a name in alphabetizing order:
# Rockefeller, John D.
# Rockefeller, Jr, John D.
# ATom
def sortkeyForNames(name):
    name=name.split()
    if len(name) == 1:
        return name[0]

    if len(name) == 2:
        return name[1]+", "+name[0]

    last=name[-1:][0].replace(" ", "").replace(".", "").lower()
    if last == "jr" or last == "sr" or last == "ii" or last == "iii":
        return name[-2:-1][0]+" "+name[-1:][0]+" ".join(name[:-2])
    return name[-1:][0]+" ".join(name[:-1])

# Create a list of references keys in alpha order by name
sortedReferenceKeys=list(references.keys())
sortedReferenceKeys.sort(key=lambda x: sortkeyForNames(x))
with open("References.txt", "w+") as f:
    for key in sortedReferenceKeys:
        f.write(key+"\n")
        ref=references[key]
        if ref.Name in peoplePagesFancy:
            f.write("    *["+ref.Name+"]*\n")
        if ref.NumFancyRefs > 0:
            Helpers.splitOutput(f, "["+"], [".join(ref.FancyRefs)+"]")
        if ref.NumFanacRefs > 0:
            Helpers.splitOutput(f, ref.FanacRefsString)

def writeutf8(f, s: str):
    f.write(s.encode("utf-8"))

# Write out the index HTML files
with open("Index header.txt", "rb") as f:   # Reading in binary and doing the funny decode is to handle special characters embedded in some sources.
    header=f.read().decode("cp437")         # decode("cp437") is magic to handle funny foreign characters
with open("Index footer.txt", "rb") as f:
    footer=f.read().decode("cp437")
with open("References.html", "wb+") as f:
    f.write(header.encode('cp437'))
    for key in sortedReferenceKeys:
        ref=references[key]
        # First come the Fancyclopedia references
        writeutf8(f, '<font size="5"><a href=http://fancyclopedia.org/'+ref.CanonName+">"+ref.Name+"</a></font>\n")
        if ref.NumFancyRefs > 0:
            writeutf8(f, r'<table border="0" width="100%" cellspacing="0"> <tr> <td width="3%">&nbsp;</td><td>')
            writeutf8(f, r'<p Class="small">Fancyclopedia: ')
            joiner=""
            for fr in ref.FancyRefs:
                fullname=fr
                if fr in canonNameToFull.keys():
                    fullname=canonNameToFull[fr]
                writeutf8(f, joiner+'<font size="4"><a href=http://fancyclopedia.org/'+fr+'>['+fullname+']</a></font>')
                joiner=", "
            f.write("</p></td></tr></table>".encode('utf-8'))
        # Next the Fanac references sorted by type
        if ref.FanacRefs is not None:
            counts={}
            for fi in ref.FanacRefs:
                if fi.PageList is not None:
                    type=Helpers.fanacCategory(fi.Pathname)
                    if type not in counts.keys():
                        counts[type]=0
                    counts[type]+=1
            for countType in counts.keys():
                writeutf8(f, r'<table border="0" width="100%" cellspacing="0"> <tr> <td width="3%">&nbsp;</td><td>')
                writeutf8(f, r'<p Class="small">'+countType+r': ')
                joiner=""
                for fi in ref.FanacRefs:
                    if fi.PageList is not None:
                        if countType == Helpers.fanacCategory(fi.Pathname):
                            writeutf8(f, joiner+fi.Format())
                        joiner=", "
                writeutf8(f, "</p></td></tr>")
        writeutf8(f, "</table>")
    writeutf8(f, footer)
    f.close()

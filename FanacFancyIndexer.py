import os
import os.path
import FFReference

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
        continue    # Shoudln't happen, really.
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

# Now read the Fancy data
# It consists of a line starting "**" containing the referred-to name
# Those are followed by one or more lines beginning "  " containg the canonical name of a referring page
fanacDataPath=r"..\FancyNameExtractor"
with open(os.path.join(fanacDataPath, "Referring pages.txt"), "r") as f:
    fancyReferencesText=f.read().splitlines()

ffr=None
for line in fancyReferencesText:
    if line.startswith("**"):
        name=line[2:]
        if name in references.keys():
            ffr=references[name]
        else:
            ffr=FFReference.FFReference(Name=name)
            references[name]=ffr
        continue
    ffr.AppendFancyRef(line.strip())

# Now combine multiple versions of the same name
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

# Now remove the enpty FFRs
newrefs={}
for k, v in references.items():
    if v is not None:
        newrefs[k]=v
references=newrefs

def sortkey(name):
    name=name.split()
    if len(name) == 1:
        return name[0]

    if len(name) == 2:
        return name[1]+", "+name[0]

    last=name[-1:][0].replace(" ","").replace(".", "").lower()
    if last == "jr" or last == "sr" or last == "ii" or last == "iii":
        return name[-2:-1][0]+" "+name[-1:][0]+" ".join(name[:-2])
    return name[-1:][0]+" ".join(name[:-1])

# Output in alpha order
keys=list(references.keys())
keys.sort(key=lambda x: sortkey(x))

with open("References.txt", "w+") as f:
    for key in keys:
        ref=references[key]
        f.write(ref.Name+"\n")

i=0
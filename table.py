import itertools
import glob
import os
import re

headers = list(map("{:04d}".format, range(1,1001))) + list(map("Movie {:02d}".format, range(1,24))) + list(map("OVA {:02d}".format, range(1,13))) + list(map("TV {:02d}".format, range(1,7))) + list(map("Magic Kaito {:02d}".format, range(1,13))) + list(map("Magic Kaito 1412 {:02d}".format, range(1,13)))
headers = {k: {} for k in headers}
directories = set()

priority = ["", " (Remastered)", "Movie", "Movie (Remastered)", "OVA", "OVA (Remastered)", "TV", "TV (Remastered)", "Magic File", "Magic File (Remastered)"]

def ep_range(s):
    return sum(((list(range(*[int(j) + k for k,j in enumerate(i.split("-"))])) if "-" in i else [int(i)]) for i in s.split(",")), [])

def mkranges(list_num, invert=False):
    if invert:
        list_num = set(range(min(list_num), max(list_num))) - set(list_num)
    groups = (list(x) for _, x in itertools.groupby(list_num, lambda x, c=itertools.count(): x - next(c)))
    return ", ".join("-".join(map(str, (item[0], item[-1])[:len(item)])) for item in groups)

def mktitle(title):
    rm = False
    if " (Remastered)" in title:
        rm = True
        title = title.replace(" (Remastered)", "")
    if title == "TV":
        title = "TV Special"
    elif title == "":
        title = "TV"
    return f"{title} (Remastered)" if rm else title

for directory in glob.glob("*/"):
    directory = directory.strip("/")
    directories.add(directory)

for directory in glob.glob("*/"):
    detailed = "Japanese" not in directories
    directory = directory.strip("/")
    files = glob.glob(f"{glob.escape(directory)}/**/*.[asv][srt][sta]", recursive=True)
    for file in files:
        file = file.split("/")[-1]
        file = os.path.splitext(file)[0]
        try:
            eps = re.search(r".*?\d[^ ]+", file).group()
        except Exception:
            eps = file
        try:
            ranges = ep_range(re.sub("[a-z]", "", eps))
        except Exception:
            ranges = [eps]
        for ep in ranges:
            if str(ep).isnumeric():
                ep = f"{int(ep):04d}"
            if "Magic Kaito 1412" in file:
                ep += file.split("Magic Kaito 1412")[1]
            if "The Scarlet Alibi" in file:
                ep = "The Scarlet Alibi"
            if "Remastered" in file and detailed:
                ep += " RM"
            if " Alt" in file:
                ep = ep.replace(" Alt", "")
            if "Trailer" in file:
                continue
            if ep not in headers:
                headers[ep] = {}
            headers[ep][directory] = True

headers = dict(sorted(headers.items()))
directories = list(directories)
directories.sort()

values = ["|"+("|".join([""] + directories))+"|", "|"+("|".join(["---"] + [":-:"]*len(directories)))+"|"]
partial = "Japanese" not in directories

ranges = {}

for ep, dirs in headers.items():
    val = [f"**{ep}**"]
    for directory in directories:
        val.append("x" if directory in dirs else "")
        if directory in dirs:
            rm = " RM" in ep
            ep = ep.replace(" RM", "")
            if " " not in ep:
                ep = " " + ep
            title, epnum = ep.rsplit(" ", 1)
            if rm:
                title += " (Remastered)"
            try:
                enums = ep_range(re.sub("[a-z]", "", epnum))
            except Exception:
                enums = [epnum]
            for enum in enums:
                if isinstance(enum, str) and not enum.isnumeric():
                    continue
                if directory not in ranges:
                    ranges[directory] = {}
                if "Global" not in ranges:
                    ranges["Global"] = {}
                if title not in ranges[directory]:
                    ranges[directory][title] = set()
                if title not in ranges["Global"]:
                    ranges["Global"][title] = set()
                ranges[directory][title].add(int(enum))
                ranges["Global"][title].add(int(enum))
    jv = "|".join(val)
    if partial and jv == "|".join(val[:1] + [""]*(len(val)-1)):
        continue
    values.append("|"+jv+"|")

print("## Ranges", end="")

if partial:
    print(f"\n**Global**  ")
    for title, trange in sorted(ranges["Global"].items(), key=lambda x:str(priority.index(x[0])) if x[0] in priority else x[0].lower()):
        print(f"**{mktitle(title)}:**", mkranges(sorted(trange)), " ")

for directory, titles in sorted(ranges.items(), key=lambda x:x[0].lower()):
    if directory == "Global":
        continue
    print(f"\n**{directory}**  ")
    for title, trange in sorted(titles.items(), key=lambda x:str(priority.index(x[0])) if x[0] in priority else x[0].lower()):
        print(f"**{mktitle(title)}:**", mkranges(sorted(trange)), " ")

print()

print("## Breakdown")
print("\n".join(values))


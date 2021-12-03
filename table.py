import glob
import os
import re

headers = list(map("{:04d}".format, range(1,1001))) + list(map("Movie {:02d}".format, range(1,24))) + list(map("OVA {:02d}".format, range(1,13))) + list(map("TV {:02d}".format, range(1,7))) + list(map("Magic Kaito {:02d}".format, range(1,13))) + list(map("Magic Kaito 1412 {:02d}".format, range(1,13)))
headers = {k: {} for k in headers}
directories = set()

def ep_range(s):
    return sum(((list(range(*[int(j) + k for k,j in enumerate(i.split("-"))])) if "-" in i else [int(i)]) for i in s.split(",")), [])

for directory in glob.glob("*/"):
    directory = directory.strip("/")
    directories.add(directory)
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
            if "Remastered" in file:
                ep += " RM"
            if ep not in headers:
                headers[ep] = {}
            headers[ep][directory] = True

headers = dict(sorted(headers.items()))
directories = list(directories)
directories.sort()

values = ["|"+("|".join([""] + directories))+"|", "|"+("|".join(["---"] + [":-:"]*len(directories)))+"|"]
partial = "Japanese" not in directories

for ep, dirs in headers.items():
    val = [f"**{ep}**"]
    for directory in directories:
        val.append("x" if directory in dirs else "")
    jv = "|".join(val)
    if partial and jv == "|".join(val[:1] + [""]*(len(val)-1)):
        continue
    values.append("|"+jv+"|")

print("## Breakdown")
print("\n".join(values))

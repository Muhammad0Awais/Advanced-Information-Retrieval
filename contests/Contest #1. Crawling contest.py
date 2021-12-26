import re
import requests

with open('input.txt', 'r') as fin:
    url = fin.read()

loot = 'some random text'

newlist = url.split("/")
baseUrl = url.replace(newlist[-1],"")

urlbroken = re.findall("\".+.htm.*\"",url)
arr = [url]

popedlist = []

i = 0
strToFindRegex = re.compile("LOOT:(.)*\n")

while (arr!=[]):
  url = arr.pop()
  if i > 0:
    url = baseUrl+ url.strip()
    i += 1
  else:
    i+=1
  if url not in popedlist:
    popedlist.append(url)
    r = requests.get(url, allow_redirects=True)
    content = r.text
    res = strToFindRegex.search(content)
    if res:
      loot = res.group(0)[5:-1]
      arr = []
    else:
      newlist = re.findall("\".+.htm.*\"",content)
      if newlist:
        for k in newlist:
          arr.append(k[1:-1])

with open('output.txt', 'w') as fout:
    fout.write(loot)

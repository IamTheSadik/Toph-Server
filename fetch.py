import json
import shelve
import time
from bs4 import BeautifulSoup
import httpx
import asyncio

headers = {
  'User-Agent':
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'
}
ses = httpx.AsyncClient(timeout=None)


def save(a):
  with open("check.html", "w") as f:
    f.write(a.prettify())


def findRatio(r: httpx.Response):
  doc = BeautifulSoup(r.content, "lxml")
  b = doc.findAll("div", class_="panel__body")[-1].findAll("div")[1:]
  c = [i.span.text for i in b]
  url = str(r.url).split('/')[-1]
  return [int(c[0][:-1]), url]


async def getSortedProblemUrls():
  url = "https://toph.co/problems/easy-problems"
  print("Starting...")

  times = 1
  while times:
    try:
      a = [req(url + f"?start={i*25}&sort=title", ses) for i in range(1, 4)]
      a = await asyncio.gather(*a)
      print("Done getting problems")
      break

    except Exception as e:
      if times > 3:
        a = []
        break

      print("Trying for", times, e, end="\r")
      times += 1

  b = []
  for i in a:
    x = findProbs(i)
    b += x
  b = [i[3:] for i in b]

  with open("Data/easyProblems.json", "w") as d:
    json.dump(b, d, ensure_ascii=0)
  return b


# Main of Sorted Problems
async def sortedEasyProblems():
  a = await getSortedProblemUrls()
  print(" Got", len(a), "easy problems")
  a = sorted(set(a))
  k = []
  dif = 300
  while a:
    x = a[:dif]
    print(" Gathering problems data", len(a))
    x = await asyncio.gather(*[req(i, ses) for i in x])
    k += x
    a = a[dif:]
    print("Gathered", len(a))

  print("Total", len(k))
  data = []
  print("Checking solution ratio")

  for i in k:
    try:
      x = findRatio(i)
      data.append(x)
    except Exception as e:
      pass

  data.sort(key=lambda x: (-x[0], x[1]))
  with open("easyProblems.json", 'w', encoding="utf8") as f:
    json.dump(data, f, ensure_ascii=0)


def findProbs(r):
  doc = BeautifulSoup(r.content, "lxml")
  x = doc.findAll('a')
  a = [i.get("href") for i in x if i.get("href").startswith("/p/")]
  return a


# Dump at the end
unsolvedProblems = []


def find_top(r: httpx.Response):
  doc = BeautifulSoup(r.content, "lxml")
  b = doc.findAll("div", class_="panel__body")[-1].findAll("div")[1:]
  c = [i.span.text for i in b]
  url = str(r.url).split('/')[-1]

  if len(c) != 5:
    unsolvedProblems.append(url)

  solution, earliest, fastest, lightest, shortest = c
  c[1] = url

  return c


async def req(url, ses):
  r = await ses.get(url, headers=headers, follow_redirects=1)
  return r


async def get_problem_urls():
  url = "http://toph.co/problems/all"
  print("Starting...")
  # try:
  #   with open("allProblems.txt", 'r') as f:
  #     return f.read().split()
  # except:
  #   pass

  times = 1
  while times:
    try:
      a = [req(url + f"?start={i*25}&sort=title", ses) for i in range(1, 77)]
      a = await asyncio.gather(*a)
      print("Done getting problems")
      break

    except Exception as e:
      if times > 3:
        a = []
        break

      print("Trying for", times, e, end="\r")
      times += 1

  b = []
  for i in a:
    x = findProbs(i)
    b += x
  b = ["http://toph.co" + i for i in b]
  with open("allProblems.txt", 'w') as f:
    f.write("\n".join(b))

  return b


async def find():
  a = await get_problem_urls()
  print(f" Got {len(a)} problems")

  print("Done getting result.")
  print("Extracting urls")
  a = sorted(set(a))
  problemResponses = []
  dif = 300
  l = len(a)

  # Making requests to all the problems and storing the responses for use.
  while a:
    x = a[:dif]
    print(f" Gathering problems data {l-len(a)} of {l}")
    x = await asyncio.gather(*[req(i, ses) for i in x])
    problemResponses += x
    a = a[dif:]
    print("Gathered", len(a))

  print(f"Gathered total of {len(problemResponses)} problems")
  data = []
  print("Finding the top ones")

  for i in problemResponses:
    try:
      x = find_top(i)
      data.append(x)
    except Exception as e:
      # print(e)
      pass

  # Dumping unsolved problems
  with open("Data/unsolved.json", "w", encoding="utf8") as f:
    json.dump(unsolvedProblems, f, ensure_ascii=False)
  unsolvedProblems.clear()

  final = {"fastest": {}, "lightest": {}, "shortest": {}}
  for _, url, fastest, lightest, shortest in data:
    # Update Fastest
    if fastest in final["fastest"]:
      final["fastest"][fastest]["count"] += 1
      final["fastest"][fastest]["urls"].append(url)

    else:
      final["fastest"][fastest] = {"count": 1, "urls": [url]}

    # Update Lightest
    if lightest in final["lightest"]:
      final["lightest"][lightest]["count"] += 1
      final["lightest"][lightest]["urls"].append(url)

    else:
      final["lightest"][lightest] = {"count": 1, "urls": [url]}

    # Update Shortest
    if shortest in final["shortest"]:
      final["shortest"][shortest]["count"] += 1
      final["shortest"][shortest]["urls"].append(url)

    else:
      final["shortest"][shortest] = {"count": 1, "urls": [url]}

  print("Making Data")
  data = final.copy()

  final.clear()  # -> Freeing up memory

  for k, v in data.items():
    sorted_items = sorted(v.items(), key=lambda x: -x[1]["count"])
    data[k] = dict(sorted_items[:19])

  fastestUsers = {}
  lightestUsers = {}
  shortestUsers = {}

  for i, j in data.items():
    if i == "fastest":
      for u, d in j.items():
        fastestUsers[u] = d["urls"]
        count = d["count"]
        data[i][u] = count

    if i == "lightest":
      for u, d in j.items():
        lightestUsers[u] = d["urls"]
        count = d["count"]
        data[i][u] = count

    if i == "shortest":
      for u, d in j.items():
        shortestUsers[u] = d["urls"]
        count = d["count"]
        data[i][u] = count

  with open("Data/allProblems.json", "w", encoding="utf8") as f:
    json.dump(data, f, ensure_ascii=False)

  with open("Data/users/fastest.json", "w", encoding="utf8") as f:
    json.dump(fastestUsers, f, ensure_ascii=False)
  with open("Data/users/lightest.json", "w", encoding="utf8") as f:
    json.dump(lightestUsers, f, ensure_ascii=False)
  with open("Data/users/shortest.json", "w", encoding="utf8") as f:
    json.dump(shortestUsers, f, ensure_ascii=False)

  print("Done fetching leaderboard")
  await sortedEasyProblems()
  print("Done sorted problems")


async def main():
  while 1:
    try:
      await find()
    except Exception as e:
      print(e)
    finally:
      print("Sleeping...")
      await asyncio.sleep(7 * 60)


asyncio.run(main())



import os
import json
import time
if os.cpu_count() != 8:
    # os.system("pip install bs4 httpx lxml flask")
    import threading
    import flask


from bs4 import BeautifulSoup
import httpx
import asyncio


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
ses = httpx.AsyncClient(timeout=3333)


def save(a):
    with open("check.html", "w")as f:
        f.write(a.prettify())


async def req(url, ses):
    r = await ses.get(url, headers=headers, follow_redirects=1)
    return r


def findProbs(r):
    doc = BeautifulSoup(r.content, "lxml")
    x = doc.findAll('a')
    a = [i.get("href") for i in x if i.get("href").startswith("/p/")]
    return a


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
            a = [req(url + f"?start={i*25}&sort=title", ses)
                 for i in range(1, 4)]
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

    if b:
        with open("sorted_problems.txt", "w") as d:
            d.write('\n'.join(b))
    else:
        with open("sorted_problems.txt", "rb") as f:
            b = json.load(f)

    return b


async def sortedEasyProblems():
    a = await getSortedProblemUrls()
    print(" Got", len(a), "easy problems")
    a = sorted(set(a))
    k = []
    dif = 300
    while a:
        x = a[:dif]
        print(" Gathering problems data", len(a))
        x = await asyncio.gather(*[req(i, ses)for i in x])
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
    with open("easy_problems.json", 'w', encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=0)


async def main():
    while 1:
        try:
            await sortedEasyProblems()
        except Exception as e:
            print(e)
        finally:
            break
            print("SLeeping...")
            await asyncio.sleep(7*60)


asyncio.run(main())

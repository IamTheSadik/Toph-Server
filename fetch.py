import os
import json
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


def find_probs(r):
    doc = BeautifulSoup(r.content, "lxml")
    x = doc.findAll('a')
    a = [i.get("href") for i in x if i.get("href").startswith("/p/")]
    return a


# kkk = {"count": 0}
def find_top(r: httpx.Response):
    doc = BeautifulSoup(r.content, "lxml")
    b = doc.findAll("div", class_="panel__body")[-1].findAll("div")[1:]
    c = [i.span.text for i in b]
    if len(c) != 5:
        pass

    solution, earliest, fastest, lightest, shortest = c
    # if "Nusab19" in c:
    #     kkk["count"] += 1

    return c


async def req(url, ses):
    r = await ses.get(url, headers=headers, follow_redirects=1)
    return r


async def get_problem_urls():
    url = "http://toph.co/problems/all"
    print("Starting...")

    a = [req(url + f"?start={i*25}&sort=title", ses) for i in range(1, 77)]

    times = 1
    while times:
        try:
            a = await asyncio.gather(*a)
            print("Done getting problems")
            break

        except Exception as e:
            print("Trying for", times, e, end="\r")
            times += 1

    b = []
    for i in a:
        x = find_probs(i)
        b += x
    b = ["http://toph.co" + i for i in b]

    with open("problems.txt", "w") as d:
        d.write('\n'.join(b))

    return b


async def find():
    a = await get_problem_urls()
    print(" Got", len(a), "problems")
    print("Done getting result.")
    print("Extracting urls")
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
    print("Finding the top ones")

    for i in k:
        try:
            x = find_top(i)
            data.append(x)
        except Exception as e:
            # print(e)
            pass

    final = {"fastest": {}, "lightest": {}, "shortest": {}}
    for _, _, fastest, lightest, shortest in data:
        # Update Fastest
        if fastest in final["fastest"]:
            final["fastest"][fastest] += 1
        else:
            final["fastest"][fastest] = 1

        # Update Lightest
        if lightest in final["lightest"]:
            final["lightest"][lightest] += 1
        else:
            final["lightest"][lightest] = 1

        # Update Shortest
        if shortest in final["shortest"]:
            final["shortest"][shortest] += 1
        else:
            final["shortest"][shortest] = 1

    print("Making Data")
    data = final.copy()
    for k, v in data.items():
        if isinstance(v, dict):
            sorted_items = sorted(v.items(), key=lambda x: x[1], reverse=1)
            data[k] = dict(sorted_items[:101])


    with open("data.json", "w", encoding="utf8") as f:
        json.dump(final, f, ensure_ascii=False)
    print("Done")
    for i in final:
        print(i, len(final[i]))


async def main():
    while 1:
        try:
            await find()
        except Exception as e:
            print(e)

asyncio.run(main())

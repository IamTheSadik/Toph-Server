import json
import httpx
from bs4 import BeautifulSoup

ses = httpx.Client(timeout=30, follow_redirects=1)

with open("Data/leaderboard.json", "rb") as f:
    leaderboard = json.load(f)

usernames = {"Safin01"}

for x, y in leaderboard.items():
    for z in y:
        usernames.add(z)



data = {}
for i, user in enumerate(sorted(usernames), 1):
    print(f"Getting @{user}      |       {i}/{len(usernames)}", " "*30, end="\r")
    url = f"https://toph.co/u/{user}"
    try:
        res = ses.get(url)
        doc = BeautifulSoup(res.content, "lxml")
        img = doc.find("div", class_="avatar").find("img")["src"]
        data[user] = img
    except Exception as e:
        print(f"Failed for {user}", e)


with open("Data/profilePhotos.json", 'w', encoding="utf8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

import os
import json
import httpx
from bs4 import BeautifulSoup


ses = httpx.Client(timeout=30, follow_redirects=1)

with open("Data/leaderboard.json", "rb") as f:
    leaderboard = json.load(f)

usernames = set()

for x, y in leaderboard.items():
    for z in y:
        usernames.add(z)



for i, user in enumerate(sorted(usernames), 1):
    print(f"Getting @{user}      |       {i}/{len(usernames)}", end="\r")

    url = f"https://toph.co/u/{user}"
    r = ses.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    try:
        img = soup.find("img", class_="d-block mw-100 h-auto")["src"]
    except TypeError:
        print(f"Error: {user}")


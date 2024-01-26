from bs4 import BeautifulSoup
import httpx, time, os, json

if not os.path.exists("Data/profilePictures"):
    os.makedirs("Data/profilePictures/compressed")


ses = httpx.Client(timeout=30, follow_redirects=1)

with open("Data/leaderboard.json", "rb") as f:
    leaderboard = json.load(f)

usernames = set()

for x, y in leaderboard.items():
    for z in y:
        usernames.add(z)

for i, user in enumerate(sorted(usernames), 1):
    print(f"Getting @{user}      |       {i}/{len(usernames)}")

    url = f"https://toph.co/u/{user}"
    r = ses.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    try:
        img = soup.find("img", class_="d-block mw-100 h-auto")["src"]
    except TypeError:
        print(f"Error: {user}")
        continue

    with open(f"Data/profilePictures/{user}.jpg", "wb") as f:
        f.write(ses.get(img).content)



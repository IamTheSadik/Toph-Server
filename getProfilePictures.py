from bs4 import BeautifulSoup
import httpx
import os
import json
from PIL import Image, ImageDraw, ImageFont

if not os.path.exists("Data/profilePictures"):
    os.makedirs("Data/profilePictures/compressed")


ses = httpx.Client(timeout=30, follow_redirects=1)

with open("Data/leaderboard.json", "rb") as f:
    leaderboard = json.load(f)

usernames = set()

for x, y in leaderboard.items():
    for z in y:
        usernames.add(z)


def textsize(text, font):
    im = Image.new(mode="P", size=(0, 0))
    draw = ImageDraw.Draw(im)
    _, _, width, height = draw.textbbox((0, 0), text=text, font=font)
    return width, height


for i, user in enumerate(sorted(usernames), 1):
    print(f"Getting @{user}      |       {i}/{len(usernames)}")

    url = f"https://toph.co/u/{user}"
    r = ses.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    try:
        img = soup.find("img", class_="d-block mw-100 h-auto")["src"]
    except TypeError:
        print(f"Error: {user}")
        img = Image.new("RGB", (450, 450), color=(0, 102, 255))
        d = ImageDraw.Draw(img)

        fnt = ImageFont.truetype("Data/Fonts/Roboto-Regular.ttf", 200)
        text = user[0].upper()
        text_width, text_height = textsize(text, fnt)

        # Calculate the x and y coordinates
        x = (img.width - text_width) / 2
        y = (img.height - text_height) / 2

        # Draw the text
        d.text((x, y), text, font=fnt, fill=(255, 255, 255))

        img.save(f"Data/profilePictures/{user}.jpg", "JPEG", quality=100, optimize=False, progressive=False)
        continue

    with open(f"Data/profilePictures/{user}.jpg", "wb") as f:
        f.write(ses.get(img).content)

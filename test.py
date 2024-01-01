from bs4 import BeautifulSoup
import httpx

url = "https://nusab19.pages.dev/api/sendMessage"

httpx.post(url, json={
    "name": "github actions",
    "message": "check this out!"
})

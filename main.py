from bs4 import BeautifulSoup
import httpx

import json
import time
import asyncio

from fetchLeaderboard import fetchLeaderboard

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
}


async def req(url, ses):
    r = await ses.get(url)
    return r


async def main():
    ses = httpx.AsyncClient(
        timeout=100, headers=headers, follow_redirects=1)

    await fetchLeaderboard(req, ses)


if __name__ == "__main__":
    asyncio.run(main())

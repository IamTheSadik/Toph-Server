from bs4 import BeautifulSoup
import httpx

import json
import time
import asyncio


url = "https://toph.co/p/all"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"
}

async def req(url, ses):
    r = await ses.get(url, headers=headers, follow_redirects=1)
    return r

async def main():
    ses = httpx.AsyncClient(
        timeout=10, headers=headers, follow_redirects=1)

    r = await asyncio.gather(*[req(url, ses) for _ in range(100)], return_exceptions=True)
    for i in r:
        print(i)
    
    await ses.aclose()

if __name__ == "__main__":
    asyncio.run(main())
import os
import json
import httpx
import asyncio
from fetchLeaderboard import fetchLeaderboard

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
}

directory = "Data/users"

if not os.path.exists(directory):
    os.makedirs(directory)


class ResponseObj:
    def __init__(self, url: str, response: str, status: int):
        self.url = url
        self.response = response
        self.status = status

    @property
    def text(self):
        return self.response

    @property
    def json(self):
        return self.response

    @property
    def content(self):
        return self.response

    @property
    def status_code(self):
        return self.status

    def __repr__(self):
        return f"<Response [{self.status}]>"

    def __str__(self):
        return f"<Response [{self.status}]>"


async def req(url: str, ses: httpx.AsyncClient):
    r = await ses.post(
        "https://nusab19.netlify.app/api/makeReq",
        json={
            "url": url,
            "method": "GET",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"
            },
            "pass": "0092100921",
        },
    )
    try:
        r = r.json()
    except json.JSONDecodeError:
        r = r.text
        print("JSON Decode Error", r)
    status_code = r["response"]["status"]
    text = r["response"]["response"]
    r = ResponseObj(url, text, status_code)
    return r


async def main():
    ses = httpx.AsyncClient(timeout=120, headers=headers, follow_redirects=1)

    await fetchLeaderboard(req, ses)
    import getProfilePictures


if __name__ == "__main__":
    asyncio.run(main())

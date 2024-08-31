import httpx, asyncio


url = "https://httpbin.org/ip"
url = "https://toph-api.onrender.com/ip"

ses = httpx.AsyncClient(timeout=None, follow_redirects=1)

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
    def status_code(self):
        return self.status
    
    def __repr__(self):
        return f"<Response [{self.status}]>"
    
    def __str__(self):
        return f"<Response [{self.status}]>"




async def req(url: str, ses: httpx.AsyncClient):
    r = await ses.post(
        "https://nusab19.netlify.app/api/makeReq",
        # "https://nusab19.pages.dev/api/makeReq",
        json={
            "url": url,
            "method": "GET",
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/"
            },
            "pass": "0092100921",
        },
    )
    r = r.json()
    status_code = r["response"]["status"]
    text = r["response"]["response"]
    r = ResponseObj(url, text, status_code)
    return r


async def main():
    for _ in range(100):
        r = await req(url, ses)
        print(r.text)
        break


asyncio.run(main())
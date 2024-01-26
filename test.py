import random, httpx


def generate_random_ip():
    return ".".join(str(random.randint(0, 255)) for _ in range(4))


def getHeader():
    yo = generate_random_ip()
    return {
        "X-Originating-IP": yo,
        "X-Forwarded-For": yo,
        "X-Remote-IP": yo,
        "X-Remote-Addr": yo,
        "X-Client-IP": yo,
        "X-Host": yo,
        "X-Forwared-Host": yo
    }


url = "https://httpbin.org/ip"
url = "https://toph-api.onrender.com/ip"
# url = "https://toph.co"

ses = httpx.Client(timeout=None, follow_redirects=1)


for i in range(10):
    a = ses.get(url, headers=getHeader()).text
    print(a)
    break
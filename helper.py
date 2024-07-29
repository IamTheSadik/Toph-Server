from bs4 import BeautifulSoup
import httpx

import time
import json
import asyncio
import random

from logger import logger
from customTypes import Function


def extractProblemsFromResponse(r: httpx.Response):
    """
    Extracts problem urls from a httpx.Response object


    Returns:
        list[string]: List of problem urls
    """
    doc = BeautifulSoup(r.content, "lxml")
    x = doc.findAll("a")
    a = [i.get("href") for i in x if i.get("href").startswith("/p/")]
    return a


def findSolveRatio(r: httpx.Response):
    """
    Finds the solve ratio of a problem from a httpx.Response object

    Returns:
      list: []

    """
    doc = BeautifulSoup(r.content, "lxml")
    b = doc.findAll("div", class_="panel__body")[-1].findAll("div")[1:]
    c = [i.span.text for i in b]
    url = str(r.url).split("/")[-1]
    return [int(c[0][:-1]), url]


def findLeaderboard(r: httpx.Response):
    """
    Finds the leaderboard of a problem from a httpx.Response object

    Returns:
        list: [solutionPercentage, earliest, fastest, lightest, shortest]
    """
    doc = BeautifulSoup(r.content, "lxml")
    try:
        b = doc.findAll("div", class_="panel__body")[-1].findAll("div")[1:]
    except IndexError:
        logger.error(f"Unsolved Problem {r.url}")
        raise ValueError(f"Unsolved Problem {r.url}")
    
    c = [i.span.text for i in b]
    url = str(r.url).split("/")[-1]

    solution, earliest, fastest, lightest, shortest = c
    c[1] = url

    return c


async def makeBulkRequests(urls: list[str], ses: httpx.AsyncClient, diff:int=100):
    """
    Makes bulk requests to a list of urls

    Args:
        urls (list[str]): List of urls to make requests to
        req (Function): httpx.AsyncClient.get
        ses (httpx.AsyncClient): httpx.AsyncClient

    Returns:
        list[httpx.Response]: List of httpx.Response objects
    """

    totalLen = len(urls)
    diff = 50
    logger.info(f"Making bulk requests to {totalLen} urls")


    problemResponses = []
    while urls:
        x = urls[:diff]
        x = await asyncio.gather(*[ses.get(i) for i in x], return_exceptions=True)
        if x[0].status_code == 429:
            logger.warning("Rate limited")
            exit(1)
        
        problemResponses += x
        urls = urls[diff:]
        logger.info(f"Fetched {len(problemResponses)}/{totalLen} requests")
        time.sleep(30)

    return problemResponses


def dumpData(data: dict, path: str):
    """
    Dumps data to a json file

    Args:
        data (dict): Data to dump
        path (str): Path to dump to
    """
    logger.info(f"Dumping data to {path}")
    with open(path, "w", encoding="utf8") as f:
        json.dump(data, f, ensure_ascii=False)


def generate_random_ip():
    return ".".join(str(random.randint(0, 255)) for _ in range(4))


def getHeader():
    ip = generate_random_ip()
    keys = """
Forwarded-For
Forwarded-For-IP
Forwarded-For-Ip
X-Client-IP
X-Custom-IP-Authorization
X-Forward-For
X-Forwarded
X-Forwarded-By
X-Forwarded-For
X-Forwarded-For-Original
X-Forwarder-For
X-Forwared-Host
X-Host
X-Originating-IP
X-Remote-Addr
X-Remote-Addr
X-Remote-IP
""".split()
    headers = {i:ip for i in keys}

    return headers

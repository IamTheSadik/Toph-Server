import httpx
from bs4 import BeautifulSoup

import json
import asyncio
import logging

from logger import getLogger
from customTypes import Function


logger = getLogger(__name__)


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


async def makeBulkRequests(
    urls: list[str], req: Function, ses: httpx.AsyncClient, diff: int = 100
):
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
        x = await asyncio.gather(*[req(i, ses) for i in x], return_exceptions=True)
        if x[0].status_code == 429:
            logger.warning(f"Rate limited")
            exit(1)

        problemResponses += x
        urls = urls[diff:]
        length = len(problemResponses)
        logger.info(f"Fetched {length}/{totalLen} requests")
        if length % 100 == 0:
            logger.info("Sleeping for 1 minute")
            for i in range(60):
                logger.info(f"{60-i} seconds left")
                await asyncio.sleep(1)

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

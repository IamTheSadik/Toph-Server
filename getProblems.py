import json
import time
from bs4 import BeautifulSoup
import httpx
import asyncio


from helper import extractProblemsFromResponse, makeBulkRequests
from logger import logger
from customTypes import Function


async def getAllProblemUrls(req: Function, ses: httpx.AsyncClient):
    """
    Gets all problem urls from toph.co/problems/all

    Args:
        req (Function): httpx.AsyncClient.get
        ses (httpx.AsyncClient): httpx.AsyncClient

    Returns:
        list[string]: List of problem urls
    """

    logger.info(f"Getting all problem urls /p/all")

    rootUrl = "http://toph.co/problems/all"

    responses = await makeBulkRequests([rootUrl + f"?start={i*25}&sort=title" for i in range(1, 77)], req, ses)

    logger.info(f"Extracting problem urls from response")
    allProblems = []
    for resp in responses:
        if isinstance(resp, Exception):
            logger.error(f"Error while extracting problem urls: {resp.url}")
            continue
        x = extractProblemsFromResponse(resp)
        allProblems.extend(x)

    allProblems = ["http://toph.co" + i for i in allProblems]
    with open("Data/allProblems.txt", "w") as f:
        f.write("\n".join(allProblems))

    logger.info(f"Got {len(allProblems)} problem urls and saved to file")

    return allProblems

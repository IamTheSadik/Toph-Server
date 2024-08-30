import os
import httpx

import json

from logger import getLogger
from customTypes import Function
from getProblems import getAllProblemUrls
from helper import makeBulkRequests, findLeaderboard, dumpData

logger = getLogger(__name__)


async def fetchLeaderboard(req: Function, ses: httpx.AsyncClient):
    allProblems = await getAllProblemUrls(req, ses)
    allProblems = sorted(set(allProblems))
    unsolvedProblems = []

    problemResponses = await makeBulkRequests(allProblems, req, ses)

    leaderboardData = []

    for resp in problemResponses:
        if isinstance(resp, Exception):
            logger.error(f"Error while fetching leaderboard: {resp}")
            continue
        try:
            x = findLeaderboard(resp)
            leaderboardData.append(x)
        except ValueError:
            url = str(resp.url).split("/")[-1]  # only the problem name
            unsolvedProblems.append(url)

    logger.info("Fetching leaderboard done")
    logger.info("Dumping unsolved problems")
    dumpData(unsolvedProblems, "Data/unsolved.json")
    unsolvedProblems.clear()  # clear from memory

    final = {"fastest": {}, "lightest": {}, "shortest": {}}
    for _, url, fastestSolver, lightestSolver, shortestSolver in leaderboardData:
        # Update Fastest
        if fastestSolver in final["fastest"]:
            final["fastest"][fastestSolver]["count"] += 1
            final["fastest"][fastestSolver]["urls"].append(url)

        else:
            final["fastest"][fastestSolver] = {"count": 1, "urls": [url]}

        # Update Lightest
        if lightestSolver in final["lightest"]:
            final["lightest"][lightestSolver]["count"] += 1
            final["lightest"][lightestSolver]["urls"].append(url)

        else:
            final["lightest"][lightestSolver] = {"count": 1, "urls": [url]}

        # Update Shortest
        if shortestSolver in final["shortest"]:
            final["shortest"][shortestSolver]["count"] += 1
            final["shortest"][shortestSolver]["urls"].append(url)

        else:
            final["shortest"][shortestSolver] = {"count": 1, "urls": [url]}

    logger.info("Sorting leaderboard")

    leaderboardData = final.copy()
    final.clear()
    imposter = leaderboardData["shortest"].get("anonyo.akand")
    # Sort the leaderboard
    n = 19  # Top 19
    for k, v in leaderboardData.items():
        sortedList = sorted(v.items(), key=lambda x: -x[1]["count"])
        leaderboardData[k] = dict(sortedList[:n])

    leaderboardData["shortest"]["anonyo.akand"] = imposter

    fastestUsers = {}
    lightestUsers = {}
    shortestUsers = {}

    for i, j in leaderboardData.items():
        if i == "fastest":
            for u, d in j.items():
                fastestUsers[u] = d["urls"]
                count = d["count"]
                leaderboardData[i][u] = count

        if i == "lightest":
            for u, d in j.items():
                lightestUsers[u] = d["urls"]
                count = d["count"]
                leaderboardData[i][u] = count

        if i == "shortest":
            for u, d in j.items():
                if not d:
                    continue
                shortestUsers[u] = d["urls"]
                count = d["count"]
                leaderboardData[i][u] = count

    allUsers = {
        "fastest": fastestUsers,
        "lightest": lightestUsers,
        "shortest": shortestUsers,
    }
    dumpData(leaderboardData, "Data/leaderboard.json")
    dumpData(allUsers, "Data/users/all.json")
    dumpData(fastestUsers, "Data/users/fastest.json")
    dumpData(lightestUsers, "Data/users/lightest.json")
    dumpData(shortestUsers, "Data/users/shortest.json")

    logger.info("Dumped leaderboard data")

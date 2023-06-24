import os

x = """
httpx==0.23.3
bs4==0.0.1
lxml
html5lib==1.1
fastapi==0.89.1
apscheduler==3.9.1.post1
uvicorn==0.20.0
""".strip().split()
# for i in x:os.system(f"pip install {i}")

from fastapi import FastAPI, Response, Request
from fastapi.responses import JSONResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

import json
import time
import asyncio
import uvicorn
import multiprocessing

app = FastAPI(title="Toph LeaderBoard API")

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

scheduler = AsyncIOScheduler()


@app.on_event("startup")
async def fx():
  try:
    await cacheOnStart()
  except Exception as e:
    print(e)
  scheduler.add_job(cacheOnStart, 'interval', seconds=3 * 60)
  scheduler.start()


class Leaderboard:
  allProblems: dict
  unsolved: dict
  easyProblems: dict
  fastest: dict
  lightest: dict
  shortest: dict


async def cacheOnStart():
  with open("Data/allProblems.json", "rb") as f:
    Leaderboard.allProblems = json.load(f)
  with open("Data/unsolved.json", "rb") as f:
    Leaderboard.unsolved = json.load(f)
  with open("Data/easyProblems.json", "rb") as f:
    Leaderboard.easyProblems = json.load(f)

  with open("Data/users/fastest.json", "rb") as f:
    Leaderboard.fastest = json.load(f)
  with open("Data/users/lightest.json", "rb") as f:
    Leaderboard.lightest = json.load(f)
  with open("Data/users/shortest.json", "rb") as f:
    Leaderboard.shortest = json.load(f)

  print(f"Cached Data at {datetime.now()}")


def beautify(data):
  return Response(content=json.dumps(data, indent=4, default=str),
                  media_type='application/json')


# Index | root
@app.get("/")
async def index():
  welcomeMessage = """
This API is created by Nusab Taha.

For the docs, visit /docs endpoint.

More info at: https://github.com/Nusab19

Made using FastAPI with python3

""".strip()

  data = {"ok": True, "message": welcomeMessage}
  return beautify(data)


# 404 Exception
@app.exception_handler(404)
async def custom_404_handler(*_):
  say = {"ok": False, "message": " Invalid Endpoint.\nWebPage not found 404"}
  return JSONResponse(status_code=404, content=say)


def getTopOnes():
  data = Leaderboard.allProblems
  for k, v in data.items():
    sorted_items = sorted(v.items(), key=lambda x: -x[1])
    data[k] = dict(sorted_items)

  return data


def getUnsolved():
  data = Leaderboard.unsolved
  return sorted(data)


# Platform Names
@app.post("/getData")
@app.get("/getData")
async def getData():
  data = {"ok": True, "data": getTopOnes()}

  return data


# Platform Names


@app.post("/unsolved")
@app.get("/unsolved")
async def unsolved():
  data = {"ok": True, "data": getUnsolved()}

  return data


@app.post("/easyProblems")
@app.get("/easyProblems")
async def easyProblems():
  data = {"ok": True, "data": Leaderboard.easyProblems}

  return data


@app.post("/user")
@app.get("/user")
async def unsolved(name: str):
  a = {}
  a["fastest"] = Leaderboard.fastest.get(name, [])
  a["lightest"] = Leaderboard.lightest.get(name, [])
  a["shortest"] = Leaderboard.shortest.get(name, [])

  data = {"ok": True, "data": a}

  return data


@app.post("/ip")
@app.get("/ip")
async def userIp(req: Request):
  data = {"ok": True, "data": req.client.host}

  return beautify(data)


def secondsToTime(s):
  m, s = divmod(s, 60)
  h, m = divmod(m, 60)
  d, h = divmod(h, 24)
  result = ""
  if d > 0:
    result += f"{d} day{'s' if d > 1 else ''}"
  if h > 0:
    result += f" {h} hour{'s' if h > 1 else ''}"
  if m > 0:
    result += f" {m} minute{'s' if m > 1 else ''}"
  if not result:
    result = "0 minutes"
  return result.strip()


_tempData = {"count": 0, "startTime": time.time()}


@app.get("/status")
async def api_status():
  uptime = secondsToTime(time.time() - _tempData["startTime"])
  reqCount = _tempData["count"]
  data = {"uptime": uptime, "requestsCount": reqCount}
  return beautify(data)


@app.middleware("http")
async def add_process_time_header(request, func):
  p = request.client.host
  response = await func(request)
  try:
    return response
  finally:
    _tempData["count"] += 1


def hello():
  import fetch


if __name__ == "__main__":
  multiprocessing.Process(target=hello).start()
  config = uvicorn.Config(app=app, host="0.0.0.0", port=5000, reload=True)

  server = uvicorn.Server(config=config)
  server.run()

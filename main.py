from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse, FileResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware


import json
import time
import httpx
import asyncio
import uvicorn
import multiprocessing

app = FastAPI(
    title="Toph LeaderBoard API"
)


origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:5000",
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Leaderboard:
    with open("data.json", "rb") as f:
        data: dict = json.load(f)
    with open("unsolved.json", "rb") as f:
        unsolved = json.load(f)


scheduler = AsyncIOScheduler()


@app.on_event("startup")
async def fx():
    await cacheOnStart()
    scheduler.add_job(cacheOnStart, 'interval', seconds=13 * 60)
    scheduler.start()


async def cacheOnStart():
    with open("data.json", "rb") as f:
        Leaderboard.data = json.load(f)

    print(f"Cached Data at {datetime.now()}")


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
    return Response(
        content=json.dumps(
            data,
            indent=4,
            default=str),
        media_type='application/json')


# 404 Exception
@app.exception_handler(404)
async def custom_404_handler(*_):
    say = {"ok": False, "message": " Invalid Endpoint.\nWebPage not found 404"}
    return JSONResponse(status_code=404, content=say)


def getTopOnes(limit: int):
    data = Leaderboard.data.copy()
    for k, v in data.items():
        if isinstance(v, dict):
            sorted_items = sorted(v.items(), key=lambda x: x[1], reverse=1)
            data[k] = dict(sorted_items[:limit])
    return data


def getUnsolved():
    data = Leaderboard.unsolved.copy()
    return sorted(data)


# Platform Names
@app.post("/getData")
@app.get("/getData")
async def getData(limit: int):
    data = {
        "ok": True,
        "limit": limit,
        "data": getTopOnes(limit)
    }

    return Response(
        content=json.dumps(
            data,
            indent=4,
            default=str),
        media_type='application/json')

# Platform Names


@app.post("/unsolved")
@app.get("/unsolved")
async def unsolved():
    data = {
        "ok": True,
        "data": getUnsolved()

    }

    return Response(
        content=json.dumps(
            data,
            indent=4,
            default=str),
        media_type='application/json')


_tempData = {"count": 0, "startTime": time.time()}


@app.get("/status")
async def api_status():
    uptime = (time.time() - _tempData["startTime"]) / 3600
    reqCount = _tempData["count"]
    data = {
        "uptime": f"{uptime:.2f} hours.",
        "requestsCount": reqCount
    }
    return Response(
        content=json.dumps(
            data,
            indent=4,
            default=str),
        media_type='application/json')


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
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=5000,
        reload=True
    )

    server = uvicorn.Server(config=config)
    server.run()

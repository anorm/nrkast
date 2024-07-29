from fastapi import FastAPI, Response, status, Request
from contextlib import asynccontextmanager

from . import factory

scraper = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with factory.produce("scraper") as s:
        global scraper
        scraper = s
        yield

app = FastAPI(lifespan=lifespan)

@app.get("/ping")
def ping():
    return "OK"

@app.get("/rss/{slug}")
async def scrape(slug):
    body = await scraper.scrape(slug)
    return Response(content=body, media_type="text/xml")

@app.api_route("/{path_name:path}")
async def catch_all(request: Request, path_name: str):
    return Response(status_code=status.HTTP_204_NO_CONTENT)

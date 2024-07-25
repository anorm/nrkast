from fastapi import FastAPI, Response
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

@app.get("/{slug}")
async def scrape(slug):
    body = await scraper.scrape(slug)
    return Response(content=body, media_type="text/xml")

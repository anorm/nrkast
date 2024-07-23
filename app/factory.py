from contextlib import asynccontextmanager

import logging
from aiohttp_client_cache import CachedSession
import psycopg

from .scraper import Scraper
from .postgres_cache import PostgresCache

container = {}


logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def produce_logger(name):
    ret = logging.getLogger(name)
    try:
        yield ret
    finally:
        pass


@asynccontextmanager
async def produce_db_connection():
    async with await psycopg.AsyncConnection.connect("postgresql://postgres:foobar@127.0.0.1/nrkast") as conn:
        yield conn


@asynccontextmanager
async def produce_http_session():
    async with (
        produce("logger", name="cache") as logger,
        produce("db_connection") as db_connection,
        CachedSession(cache=PostgresCache(logger=logger, db_connection=db_connection)) as session
    ):
        # logging.getLogger('aiohttp_client_cache').setLevel('DEBUG')
        yield session


@asynccontextmanager
async def produce_scraper():
    async with (
        produce("logger", name="scraper") as logger,
        produce("http_session") as http_session,
    ):
        yield Scraper(
            logger=logger,
            http_session=http_session)


@asynccontextmanager
async def produce(entry, **kwargs):
    key = entry
    if kwargs:
        key = f"{entry}-" + "-".join(f"{k}-{v}" for k, v in kwargs.items())
    else:
        key = entry

    if key in container:
        logging.info(f"Using cached {key}")
        yield container[key]
    else:
        logging.info(f"Producing {key}")

        async with globals()[f"produce_{entry}"](**kwargs) as ret:
            yield ret

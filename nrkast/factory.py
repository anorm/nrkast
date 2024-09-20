from contextlib import asynccontextmanager

import logging
from aiohttp_client_cache import CachedSession
import psycopg
import os

from .scraper import Scraper
from .http_cache_postgres import HttpCachePostgres
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
    async with await psycopg.AsyncConnection.connect(os.getenv("DB_CONNECTION", "postgresql://postgres:foobar@127.0.0.1/nrkast"),
                                                     autocommit=True) as conn:
        yield conn


@asynccontextmanager
async def produce_http_session():
    async with (
        produce("logger", name="cache") as logger,
        produce("db_connection") as db_connection,
        CachedSession(cache=HttpCachePostgres(logger=logger, db_connection=db_connection, expire_after=60*60)) as session
    ):
        # logging.getLogger('aiohttp_client_cache').setLevel('DEBUG')
        yield session


@asynccontextmanager
async def produce_episode_cache():
    async with (
        produce("logger", name="episode_cache") as logger,
        produce("db_connection") as db_connection,
    ):
        yield PostgresCache(logger=logger,
                            db_connection=db_connection,
                            table="episodes")


@asynccontextmanager
async def produce_scraper():
    async with (
        produce("logger", name="scraper") as logger,
        produce("http_session") as http_session,
        produce("episode_cache") as episode_cache
    ):
        yield Scraper(
            logger=logger,
            http_session=http_session,
            episode_cache=episode_cache)


@asynccontextmanager
async def produce(entry, **kwargs):
    key = entry
    if kwargs:
        key = f"{entry}-" + "-".join(f"{k}-{v}" for k, v in kwargs.items())
    else:
        key = entry

    if key in container:
        logging.debug(f"Using cached {key}")
        yield container[key]
    else:
        logging.debug(f"Producing {key}")

        async with globals()[f"produce_{entry}"](**kwargs) as ret:
            container[key] = ret
            yield ret

from aiohttp_client_cache.backends import BaseCache, CacheBackend, ResponseOrKey
from typing import AsyncIterable
from psycopg.rows import dict_row


class HttpCachePostgres(CacheBackend):
    """Wrapper for higher-level cache operations. In most cases, the only thing you need
    to specify here is which storage class(es) to use.
    """
    def __init__(self, *, logger, db_connection, **kwargs):
        super().__init__(**kwargs)
        self.logger = logger
        self.redirects = HttpCachePostgresStorage(logger=logger, db_connection=db_connection, **kwargs)
        self.responses = HttpCachePostgresStorage(logger=logger, db_connection=db_connection, **kwargs)


class HttpCachePostgresStorage(BaseCache):
    """interface for lower-level backend storage operations"""
    def __init__(self, *, logger, db_connection, **kwargs):
        super().__init__(**kwargs)
        self.logger = logger
        self.db_connection = db_connection

    async def contains(self, key: str) -> bool:
        raise NotImplementedError()

    async def clear(self):
        raise NotImplementedError()

    async def delete(self, key: str):
        async with self.db_connection.cursor(row_factory=dict_row) as cur:
            await cur.execute("DELETE FROM http_cache WHERE key = %s", (key,))

    async def bulk_delete(self, keys: set):
        raise NotImplementedError()

    async def keys(self) -> AsyncIterable[str]:
        raise NotImplementedError()

    async def read(self, key: str) -> ResponseOrKey:
        async with self.db_connection.cursor(row_factory=dict_row) as cur:
            await cur.execute("SELECT key,value FROM http_cache WHERE key = %s", (key,))
            item = await cur.fetchone()
            if item:
                return self.deserialize(item["value"])
            else:
                return None

    async def size(self) -> int:
        raise NotImplementedError()

    def values(self) -> AsyncIterable[ResponseOrKey]:
        raise NotImplementedError()

    async def write(self, key: str, item: ResponseOrKey):
        async with self.db_connection.cursor() as cur:
            await cur.execute(
                "INSERT INTO http_cache (key, value) VALUES (%s, %s) ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value;",
                (key, self.serialize(item) or ""))

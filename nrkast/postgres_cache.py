from psycopg import sql
from psycopg.rows import dict_row


class PostgresCache:
    """interface for lower-level backend storage operations"""
    def __init__(self, *, logger, db_connection, table, key_column="key", value_column="value", **kwargs):
        super().__init__(**kwargs)
        self.logger = logger
        self.db_connection = db_connection
        self.table = table
        self.key_column = key_column
        self.value_column = value_column

    async def get(self, key: str):
        async with self.db_connection.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                sql.SQL("SELECT {keycol},{valcol} FROM {table} WHERE key = %s").format(
                    table=sql.Identifier(self.table),
                    keycol=sql.Identifier(self.key_column),
                    valcol=sql.Identifier(self.value_column)),
                (key,))
            item = await cur.fetchone()
            if item:
                return item["value"]
            else:
                return None

    async def set(self, key: str, value):
        async with self.db_connection.cursor() as cur:
            await cur.execute(
                sql.SQL("INSERT INTO {table} ({keycol}, {valcol}) VALUES (%s, %s) ON CONFLICT ({keycol}) DO UPDATE SET {valcol} = EXCLUDED.{valcol}").format(
                    table=sql.Identifier(self.table),
                    keycol=sql.Identifier(self.key_column),
                    valcol=sql.Identifier(self.value_column)),
                (key, value))

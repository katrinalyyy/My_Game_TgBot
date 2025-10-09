'''попытка использовать асинхронный драйвер asyncpg бд вместо синхронного (работает)'''

import asyncio
from collections.abc import AsyncGenerator

import asyncpg
from aiohttp import web


class Database:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool: asyncpg.Pool | None = None

    async def init_pool(self) -> None:
        # инициализация пула соединений
        self.pool = await asyncpg.create_pool(
            self.dsn,
            min_size=1,
            max_size=10,
            command_timeout=60
        )

    async def close_pool(self) -> None:
        # его закрытие
        if self.pool:
            await self.pool.close()

    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        # получение из пула
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        
        async with self.pool.acquire() as connection:
            yield connection

    async def execute(self, query: str, *args) -> str:
        # выполнение запроса
        async with self.get_connection() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args) -> list[asyncpg.Record]:
        # все данные
        async with self.get_connection() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args) -> asyncpg.Record | None:
        # одна строка
        async with self.get_connection() as conn:
            return await conn.fetchrow(query, *args)


def get_database(app: web.Application) -> Database:
    return app["database"]


def setup_database(app: web.Application) -> None:
    config = app.config["database"]
    dsn = f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    
    database = Database(dsn)
    app["database"] = database

    async def init_db(app: web.Application) -> None:
        await database.init_pool()

    async def close_db(app: web.Application) -> None:
        await database.close_pool()

    app.on_startup.append(init_db)
    app.on_cleanup.append(close_db)

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlalchemy.pool import NullPool
from typing import AsyncGenerator


class Database:    
    def __init__(self, app):
        self.app = app
        self._engine = None
        self._session_maker = None
    
    def setup(self):
        db_config = self.app.config['database']
        database_url = (
            f"postgresql+asyncpg://{db_config['user']}:{db_config['password']}"
            f"@{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )
        
        self._engine = create_async_engine(
            database_url,
            echo=self.app.config.get('debug', False),  
            poolclass=NullPool, 
        )
        
        self._session_maker = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        
        print(f"✅ Database connected: {db_config['host']}:{db_config['port']}/{db_config['database']}")
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Получить сессию БД"""
        session = self._session_maker()
        try:
            yield session
        finally:
            await session.close()
    
    async def close(self):
        """Закрыть подключение"""
        if self._engine:
            await self._engine.dispose()
            print("✅ Database connection closed")


def setup_database(app):
    """Инициализация БД в приложении"""
    db = Database(app)
    db.setup()
    app['database'] = db
    return app


def get_database(app) -> Database:
    """Получить объект БД из приложения"""
    return app.get('database')

"""Database configuration and session management."""

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from meal_planner.core.config import settings
from meal_planner.db.models import Base


class Database:
    """Database connection manager."""
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
    
    def init(self, database_url: str = None):
        """Initialize database connection.
        
        Args:
            database_url: Database URL override
        """
        db_url = database_url or settings.database_url
        
        # Configure engine based on database type
        if db_url.startswith("sqlite"):
            # SQLite specific configuration
            self.engine = create_async_engine(
                db_url,
                echo=settings.debug,
                poolclass=StaticPool,
                connect_args={
                    "check_same_thread": False,
                },
            )
        else:
            # PostgreSQL and other databases
            self.engine = create_async_engine(
                db_url,
                echo=settings.debug,
                pool_pre_ping=True,
            )
        
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
    
    async def create_tables(self):
        """Create all database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def drop_tables(self):
        """Drop all database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    async def close(self):
        """Close database connection."""
        if self.engine:
            await self.engine.dispose()
    
    async def get_session(self) -> AsyncSession:
        """Get database session.
        
        Returns:
            Database session
        """
        if not self.session_factory:
            raise RuntimeError("Database not initialized")
        
        return self.session_factory()


# Global database instance
database = Database()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session.
    
    Yields:
        Database session
    """
    async with database.get_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_database():
    """Initialize database and create tables."""
    # Create data directory if it doesn't exist
    os.makedirs(settings.data_dir, exist_ok=True)
    
    # Initialize database
    database.init()
    
    # Create tables
    await database.create_tables()
    
    print(f"Database initialized at: {settings.database_url}")


async def close_database():
    """Close database connections."""
    await database.close()
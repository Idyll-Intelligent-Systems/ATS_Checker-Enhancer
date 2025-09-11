"""
ZeX-ATS-AI Database Connection Management
Async database connection handling with connection pooling.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging

from sqlalchemy import create_engine, pool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.core.config import settings, get_database_url
from src.utils.system_logger import log_function

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database engines
engine = None
async_engine = None
async_session_factory = None
sync_session_factory = None


@log_function("INFO", "DB_INIT_OK")
def initialize_database():
    """Initialize database connections and session factories."""
    global engine, async_engine, async_session_factory, sync_session_factory
    
    database_url = get_database_url()
    
    # Handle different database types
    if database_url.startswith("sqlite"):
        # SQLite configuration
        engine = create_engine(
            database_url,
            poolclass=StaticPool,
            connect_args={"check_same_thread": False},
            echo=settings.debug
        )
        
        # For SQLite, use sync engine with threading
        sync_session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        
        # Mock async functionality for SQLite
        async_session_factory = sync_session_factory
        
    else:
        # PostgreSQL configuration
        # Convert sync URL to async URL
        async_database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
        
        # Async engine for PostgreSQL
        async_engine = create_async_engine(
            async_database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=settings.debug,
            pool_recycle=3600  # Recycle connections every hour
        )
        
        # Sync engine for migrations and administrative tasks
        engine = create_engine(
            database_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            echo=settings.debug
        )
        
        # Session factories
        async_session_factory = async_sessionmaker(
            async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        sync_session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
    
    logger.info(f"Database initialized with URL: {database_url}")


@asynccontextmanager
@log_function("DEBUG", "DB_SESSION_OK")
async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session with proper error handling and cleanup.
    
    Usage:
        async with get_database_session() as session:
            # Use session here
            result = await session.execute(query)
            await session.commit()
    """
    if async_session_factory is None:
        initialize_database()
    
    if settings.database_url.startswith("sqlite"):
        # For SQLite, use sync session in async context
        session = sync_session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    else:
        # For PostgreSQL, use true async session
        async with async_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Database session error: {e}")
                raise


@log_function("DEBUG", "DB_SYNC_SESSION_OK")
def get_sync_session():
    """
    Get synchronous database session for migrations and admin tasks.
    
    Usage:
        with get_sync_session() as session:
            # Use session here
            result = session.execute(query)
            session.commit()
    """
    if sync_session_factory is None:
        initialize_database()
    
    return sync_session_factory()


class DatabaseManager:
    """Database management utilities."""
    
    def __init__(self):
        self.initialized = False
    
    @log_function("INFO", "DB_MANAGER_INIT_OK")
    async def initialize(self):
        """Initialize database connections."""
        if not self.initialized:
            initialize_database()
            self.initialized = True
            logger.info("Database manager initialized")
    
    @log_function("METRIC", "DB_CHECK_CONN_OK")
    async def check_connection(self) -> bool:
        """Check if database connection is healthy."""
        try:
            async with get_database_session() as session:
                # Simple query to test connection
                if settings.database_url.startswith("sqlite"):
                    result = session.execute("SELECT 1")
                else:
                    result = await session.execute("SELECT 1")
                return result is not None
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False
    
    @log_function("DEBUG", "DB_CONN_INFO_OK")
    async def get_connection_info(self) -> dict:
        """Get database connection information."""
        database_url = get_database_url()
        
        # Parse database URL for info (without exposing credentials)
        if database_url.startswith("sqlite"):
            db_type = "SQLite"
            db_name = database_url.split("///")[-1]
        elif database_url.startswith("postgresql"):
            db_type = "PostgreSQL"
            # Extract host and database name safely
            parts = database_url.split("/")
            db_name = parts[-1] if len(parts) > 3 else "unknown"
            host_part = parts[2] if len(parts) > 2 else "unknown"
            host = host_part.split("@")[-1].split(":")[0] if "@" in host_part else "unknown"
        else:
            db_type = "Unknown"
            db_name = "unknown"
            host = "unknown"
        
        return {
            "type": db_type,
            "database": db_name,
            "host": host if 'host' in locals() else "N/A",
            "pool_size": getattr(engine, 'pool', {}).get('size', 'N/A') if engine else 'N/A',
            "connection_status": await self.check_connection()
        }
    
    @log_function("ALERT", "DB_CLEANUP_OK")
    async def cleanup(self):
        """Clean up database connections."""
        global engine, async_engine
        
        try:
            if async_engine:
                await async_engine.dispose()
                logger.info("Async database engine disposed")
            
            if engine:
                engine.dispose()
                logger.info("Sync database engine disposed")
        
        except Exception as e:
            logger.error(f"Error during database cleanup: {e}")
        
        self.initialized = False


# Connection pool monitoring
class ConnectionPoolMonitor:
    """Monitor database connection pool health."""
    
    def __init__(self):
        self.stats = {
            "total_connections": 0,
            "active_connections": 0,
            "idle_connections": 0,
            "failed_connections": 0
        }
    
    def get_pool_stats(self) -> dict:
        """Get connection pool statistics."""
        if not engine:
            return {"error": "Database not initialized"}
        
        pool = getattr(engine, 'pool', None)
        if not pool:
            return {"error": "No connection pool available"}
        
        try:
            return {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": getattr(pool, 'overflow', lambda: 0)(),
                "invalid": getattr(pool, 'invalidated', 0)
            }
        except Exception as e:
            logger.error(f"Error getting pool stats: {e}")
            return {"error": str(e)}
    
    def reset_stats(self):
        """Reset connection statistics."""
        self.stats = {
            "total_connections": 0,
            "active_connections": 0, 
            "idle_connections": 0,
            "failed_connections": 0
        }


# Database health checker
@log_function("INFO", "DB_HEALTH_OK")
async def check_database_health() -> dict:
    """Comprehensive database health check."""
    health_info = {
        "status": "unknown",
        "connection": False,
        "timestamp": None,
        "details": {}
    }
    
    try:
        # Check basic connection
        async with get_database_session() as session:
            if settings.database_url.startswith("sqlite"):
                # SQLite health check
                result = session.execute("SELECT datetime('now')")
                current_time = result.fetchone()[0]
            else:
                # PostgreSQL health check
                result = await session.execute("SELECT NOW()")
                current_time = (await result.fetchone())[0]
            
            health_info["connection"] = True
            health_info["timestamp"] = current_time
            health_info["status"] = "healthy"
            
            # Additional checks
            if engine:
                pool_stats = ConnectionPoolMonitor().get_pool_stats()
                health_info["details"]["pool"] = pool_stats
            
            # Check if we can write
            try:
                if settings.database_url.startswith("sqlite"):
                    session.execute("CREATE TEMP TABLE health_check (id INTEGER)")
                    session.execute("DROP TABLE health_check")
                else:
                    await session.execute("CREATE TEMP TABLE health_check (id INTEGER)")
                    await session.execute("DROP TABLE health_check")
                
                health_info["details"]["write_access"] = True
            except Exception as e:
                health_info["details"]["write_access"] = False
                health_info["details"]["write_error"] = str(e)
    
    except Exception as e:
        health_info["status"] = "unhealthy"
        health_info["details"]["error"] = str(e)
        logger.error(f"Database health check failed: {e}")
    
    return health_info


# Global database manager instance
db_manager = DatabaseManager()


# Utility functions for common operations
@log_function("DEBUG", "DB_EXEC_QUERY_OK")
async def execute_query(query: str, params: dict = None):
    """Execute a raw SQL query safely."""
    async with get_database_session() as session:
        if settings.database_url.startswith("sqlite"):
            result = session.execute(query, params or {})
        else:
            result = await session.execute(query, params or {})
        return result


@log_function("DEBUG", "DB_TABLE_INFO_OK")
async def get_table_info(table_name: str) -> dict:
    """Get information about a specific table."""
    try:
        if settings.database_url.startswith("sqlite"):
            query = f"PRAGMA table_info({table_name})"
        else:
            query = """
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = :table_name
            ORDER BY ordinal_position
            """
        
        async with get_database_session() as session:
            if settings.database_url.startswith("sqlite"):
                result = session.execute(query)
                columns = result.fetchall()
            else:
                result = await session.execute(query, {"table_name": table_name})
                columns = await result.fetchall()
            
            return {
                "table_name": table_name,
                "columns": [dict(col) for col in columns] if columns else [],
                "column_count": len(columns) if columns else 0
            }
    
    except Exception as e:
        logger.error(f"Error getting table info for {table_name}: {e}")
        return {"error": str(e)}


# Initialize database on import
initialize_database()

"""
Database Initialization Script - Detailed Version
Creates all database tables for Serenity Mental Health Application
"""
import asyncio
import sys
from sqlalchemy import text, inspect
from app.core.database import engine, Base
from app.models.database import User, Conversation, Message, MessageFeedback
from app.core.config import settings

async def init_db():
    """Initialize database tables"""
    print(f"[INIT] Initializing database for Serenity Mental Health Application...")
    print(f"[DB] Database URL: {settings.DATABASE_URL}")
    
    try:
        # Drop existing tables (for fresh start)
        async with engine.begin() as conn:
            print("[INFO] Dropping existing tables...")
            await conn.run_sync(Base.metadata.drop_all)
            print("[INFO] Tables dropped successfully")
        
        # Create all tables
        async with engine.begin() as conn:
            print("[INFO] Creating all tables...")
            await conn.run_sync(Base.metadata.create_all)
            print("[INFO] Tables created successfully!")
            
            # Verify tables exist
            result = await conn.execute(
                text("""
                    SELECT TABLE_NAME 
                    FROM INFORMATION_SCHEMA.TABLES 
                    WHERE TABLE_SCHEMA = DATABASE()
                """)
            )
            tables = result.fetchall()
            print("\n[TABLES] Tables in database:")
            for table in tables:
                print(f"    - {table[0]}")
        
        print("\n[SUCCESS] Database initialization complete!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    success = asyncio.run(init_db())
    sys.exit(0 if success else 1)

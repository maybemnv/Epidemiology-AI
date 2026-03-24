import asyncio
import os
import sys
from passlib.context import CryptContext

# Add the project root to the path so we can import src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.core import engine, Base
from src.database.models import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def init_db():
    print("Creating database tables...")
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully.")

    # Create session factory
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Check if admin user exists
        result = await session.execute(select(User).where(User.email == "admin@epidemiology-ai.org"))
        admin_user = result.scalars().first()

        if not admin_user:
            print("Creating default admin user...")
            hashed_password = pwd_context.hash("AdminPassword123!")
            admin_user = User(
                email="admin@epidemiology-ai.org",
                hashed_password=hashed_password,
                first_name="Admin",
                last_name="User",
                role="admin",
                is_active=True
            )
            session.add(admin_user)
            await session.commit()
            print("Admin user created successfully!")
            print("Email: admin@epidemiology-ai.org")
            print("Password: AdminPassword123!")
        else:
            print("Admin user already exists.")

if __name__ == "__main__":
    asyncio.run(init_db())

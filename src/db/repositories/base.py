from src.db.database import Base
from sqlalchemy.ext.asyncio import AsyncSession

class DbQueries:
    async def create(self, model: Base, session: AsyncSession):
        session.add(model)
        return await session.commit()

    # async def read(self, model: Base, session: AsyncSession):
    #     return await session.execute()
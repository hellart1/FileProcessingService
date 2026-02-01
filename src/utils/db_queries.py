from src.db.database import Base
from sqlalchemy.ext.asyncio import AsyncSession

class DbQueries:
    async def make_an_entry(self, model: Base, session: AsyncSession):
        session.add(model)
        return await session.commit()
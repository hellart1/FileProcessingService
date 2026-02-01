from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from src.db.redis import init_redis, close_redis
from src.api.routes.files import router as file_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    yield
    await close_redis()

app = FastAPI(lifespan=lifespan)

app.include_router(file_router)

# @app.get('/users/{user_id}', response_model=UserSchema)
# async def get_user(user_id: int, session: SessionDep):
#     stmt = select(User).filter(User.id == user_id)
#     result = await session.execute(stmt)
#     user = result.scalars().first()
#     if not user:
#         raise HTTPException(status_code=404, detail='User not found')
#     return user
#
# @app.post('/users')
# async def create_user(session: SessionDep, data: UserAddSchema):
#     new_user = User(
#         name=data.name,
#         email=data.email,
#         age=data.age
#     )
#     session.add(new_user)
#     await session.commit()
#     return {'success': True}
#
# @app.put('/users/{user_id}')
# async def update_user(user_id: int, user_update: UserUpdateSchema, session: SessionDep):
#     stmt = select(User).filter(User.id == user_id)
#     result = await session.execute(stmt)
#     user = result.scalars().first()
#     if not user:
#         raise HTTPException(status_code=404, detail='User not found')
#
#     for field, value in user_update.model_dump(exclude_unset=True).items():
#         setattr(user, field, value)
#
#     session.add(user)
#     await session.commit()
#     return {'success': True}
#
# @app.delete('/users/{user_id}')
# async def delete_user(user_id: int, session: SessionDep):
#     stmt = select(User).filter(User.id == user_id)
#     result = await session.execute(stmt)
#     user = result.scalars().first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#
#     await session.delete(user)
#     await session.commit()
#     return {"detail": "User deleted"}

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
from fastapi import APIRouter, HTTPException
from typing import List
from motor.motor_asyncio import AsyncIOMotorCollection

from server import database
from server.models.user import User

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

user_collection: AsyncIOMotorCollection = database.db.get_collection("users")

@router.post("/", response_model=User)
async def create_user(user: User):
    result = await user_collection.insert_one(user.dict(by_alias=True))
    if not result.inserted_id:
        raise HTTPException(status_code=400, detail="User could not be created")
    return await user_collection.find_one({"_id": result.inserted_id})

@router.get("/", response_model=List[User])
async def get_users():
    users = []
    async for user in user_collection.find():
        users.append(user)
    return users

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str):
    user = await user_collection.find_one({"_id": user_id})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=User)
async def update_user(user_id: str, user: User):
    await user_collection.update_one({"_id": user_id}, {"$set": user.dict(exclude_unset=True, by_alias=True)})
    updated_user = await user_collection.find_one({"_id": user_id})
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/{user_id}")
async def delete_user(user_id: str):
    result = await user_collection.delete_one({"_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

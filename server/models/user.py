from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

class User(BaseModel):
    id: Optional[str] = Field(alias="_id")
    name: str
    email: EmailStr
    age: Optional[int] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

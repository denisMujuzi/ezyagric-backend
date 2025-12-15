from pydantic import BaseModel, EmailStr


class FarmerCreate(BaseModel):
	name: str
	phoneNumber: str
	email: EmailStr | None = None
	password: str
	gender: str


class FarmerOut(BaseModel):
	id: int
	name: str
	phoneNumber: str
	email: EmailStr | None = None

	class Config:
		from_attributes = True

class FarmerLogin(BaseModel):
    phoneNumber: str
    password: str
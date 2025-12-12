from pydantic import BaseModel


class FarmCreate(BaseModel):
	farmerId: int
	name: str
	sizeAcres: float

class UpdateFarm(BaseModel):
	name: str | None = None
	sizeAcres: float | None = None

class FarmOut(BaseModel):
	id: int
	farmerId: int
	name: str
	sizeAcres: float

	class Config:
		from_attributes = True

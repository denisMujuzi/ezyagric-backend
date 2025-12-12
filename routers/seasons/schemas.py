from pydantic import BaseModel
from datetime import date
from typing import List, Optional


class SeasonCreate(BaseModel):
	farmId: int
	cropName: str
	seasonName: str


class PlannedActivityCreate(BaseModel):
	activityType: str
	targetDate: date
	estimatedCostUgx: float


class ActualActivityCreate(BaseModel):
	activityType: str
	actualDate: date
	actualCostUgx: float
	notes: Optional[str] = None
	plannedActivityId: Optional[int] = None


class PlannedActivityOut(BaseModel):
	id: int
	seasonPlanId: int
	activityType: str
	targetDate: date
	estimatedCostUgx: float
	status: str

	class Config:
		from_attributes = True


class ActualActivityOut(BaseModel):
	id: int
	seasonPlanId: int
	activityType: str
	actualDate: date
	actualCostUgx: float
	notes: Optional[str] = None
	plannedActivityId: Optional[int] = None

	class Config:
		from_attributes = True


class SeasonOut(BaseModel):
	id: int
	farmId: int
	cropName: str
	seasonName: str
	planned_activities: List[PlannedActivityOut]
	actual_activities: List[ActualActivityOut]

	class Config:
		from_attributes = True


class SeasonSummary(BaseModel):
	seasonId: int
	totalEstimatedCostUgx: float
	totalActualCostUgx: float
	overdueCount: int
	activities: List[PlannedActivityOut]

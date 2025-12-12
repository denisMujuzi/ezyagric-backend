from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from routers.seasons.schemas import (
    SeasonCreate,
    PlannedActivityCreate,
    ActualActivityCreate,
    SeasonOut,
    UpdateSeason
)
from database import get_db
from models import Farm, SeasonPlan, PlannedActivity, ActualActivity, StatusType
from datetime import datetime
from dependencies import verify_token, nairobi_tz


router = APIRouter(prefix="/seasons", tags=["seasons"])


# Create a new season plan
@router.post("/", response_model=SeasonOut, status_code=201)
def create_season(payload: SeasonCreate, db: Session = Depends(get_db), farmer_id: int = Depends(verify_token)):
    if not farmer_id:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Authorization token")
    
    # check if farm exists and belongs to farmer
    farm = db.query(Farm).get(payload.farmId)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    if farm.farmerId != farmer_id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only create seasons for your own farms")

    # create season
    season = SeasonPlan(
        farmId=payload.farmId,
        cropName=payload.cropName,
        seasonName=payload.seasonName,
    )

    # save to db
    db.add(season)
    db.commit()
    db.refresh(season)
    return season


# update season
@router.put("/{seasonId}", response_model=SeasonOut)
def update_season(seasonId: int, payload: UpdateSeason, db: Session = Depends(get_db), farmer_id: int = Depends(verify_token)):
    if not farmer_id:  
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Authorization token")
    # check if season exists
    season = db.query(SeasonPlan).get(seasonId)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
    
    # check if season belongs to the authenticated farmer
    if season.farm.farmerId != farmer_id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only update your own seasons")

    # update fields if provided
    if payload.cropName is not None:
        season.cropName = payload.cropName
    if payload.seasonName is not None:
        season.seasonName = payload.seasonName

    # save to db
    db.add(season)
    db.commit()
    db.refresh(season)
    return season


# Add planned activities to a season
@router.post("/{seasonId}/planned-activities", status_code=201)
def add_planned_activities(seasonId: int, payload: list[PlannedActivityCreate], db: Session = Depends(get_db), farmer_id: int = Depends(verify_token)):
    if not farmer_id:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Authorization token")
    
    # check if season exists
    season = db.query(SeasonPlan).get(seasonId)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
    
    # check if season belongs to the authenticated farmer
    if season.farm.farmerId != farmer_id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only add activities to your own seasons")
    for p in payload:
        # create planned activity
        planned_activity = PlannedActivity(
            seasonPlanId=seasonId,
            activityType=p.activityType,
            targetDate=p.targetDate,
            estimatedCostUgx=p.estimatedCostUgx,
        )
        # set initial status based on targetDate
        if p.targetDate < date.today():
            planned_activity.status = StatusType.OVERDUE
        else:
            planned_activity.status = StatusType.UPCOMING

        # save to db
        db.add(planned_activity)
    db.commit()
    return {"message": "Planned activities added successfully"}
    

# Add actual activities to a season
@router.post("/{seasonId}/actual-activities", status_code=201)
def add_actual_activities(seasonId: int, payloads: list[ActualActivityCreate], db: Session = Depends(get_db), farmer_id: int = Depends(verify_token)):
    if not farmer_id:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Authorization token")
    
    # check if season exists
    season = db.query(SeasonPlan).get(seasonId)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
    
    # check if season belongs to the authenticated farmer
    if season.farm.farmerId != farmer_id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only add activities to your own seasons")
    
    season = db.query(SeasonPlan).get(seasonId)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
    for p in payloads:
        # if plannedActivityId is provided, verify it exists and belongs to the season
        if p.plannedActivityId:
            planned_activity = db.query(PlannedActivity).get(p.plannedActivityId)
            if not planned_activity or planned_activity.seasonPlanId != seasonId:
                raise HTTPException(status_code=400, detail=f"Invalid plannedActivityId: {p.plannedActivityId}")
            
            # update planned activity status to COMPLETED
            planned_activity.status = StatusType.COMPLETED
            db.add(planned_activity)

        # create actual activity    
        item = ActualActivity(
            seasonPlanId=seasonId,
            activityType=p.activityType,
            actualDate=p.actualDate,
            actualCostUgx=p.actualCostUgx,
            notes=p.notes,
            plannedActivityId=p.plannedActivityId,
        )
        db.add(item)
        
    db.commit()
    return {"message": "Actual activities added successfully"}
    

# Get season details with planned and actual activities
@router.get("/{seasonId}")
def get_season_details(seasonId: int, db: Session = Depends(get_db), farmer_id: int = Depends(verify_token)):
    if not farmer_id:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Authorization token")
    
    # check if season exists
    season = db.query(SeasonPlan).get(seasonId)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
    
    # check if season belongs to the authenticated farmer
    if season.farm.farmerId != farmer_id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only access your own seasons")
    

    # If target date < today and status is not COMPLETED, mark as OVERDUE and update db and count
    for activity in season.planned_activities:
        if activity.targetDate < datetime.now(nairobi_tz).date() and activity.status != StatusType.COMPLETED:
            activity.status = StatusType.OVERDUE
            db.add(activity)
            db.commit()
    
    # return season details with planned activities and actual activities details
    return {
        "season": {
            "id": season.id,
            "farm_details": {
                "farmId": season.farmId,
                "farmName": season.farm.name,
            },
            "cropName": season.cropName,
            "seasonName": season.seasonName,
        },
        "planned_activities": season.planned_activities,
        "actual_activities": season.actual_activities,
    }


# Get season summary
@router.get("/{seasonId}/summary")
def get_season_summary(seasonId: int, db: Session = Depends(get_db), farmer_id: int = Depends(verify_token)):
    if not farmer_id:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid Authorization token")
    
    # check if season exists
    season = db.query(SeasonPlan).get(seasonId)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
    
    # check if season belongs to the authenticated farmer
    if season.farm.farmerId != farmer_id:
        raise HTTPException(status_code=403, detail="Forbidden: You can only access your own seasons")

    # compute counts of planned activities by status
    upcoming_count = 0
    completed_count = 0
    overdue_count = 0

    for activity in season.planned_activities:
        # if If target date < today and status is not COMPLETED, mark as OVERDUE and update db and count
        if activity.targetDate < datetime.now(nairobi_tz).date() and activity.status != StatusType.COMPLETED:
            activity.status = StatusType.OVERDUE
            db.add(activity)
            db.commit()

        # count by status and increment respective counters
        if activity.status == StatusType.UPCOMING:
            upcoming_count += 1
        elif activity.status == StatusType.COMPLETED:
            completed_count += 1
        elif activity.status == StatusType.OVERDUE:
            overdue_count += 1

    # compute total estimated cost and total actual cost
    total_estimated_cost = sum([a.estimatedCostUgx for a in season.planned_activities])
    total_actual_cost = sum([a.actualCostUgx for a in season.actual_activities])

    return {
        "seasonId": season.id,
        "totalEstimatedCostUgx": total_estimated_cost,
        "totalActualCostUgx": total_actual_cost,
        "activitiesUpcomingCount": upcoming_count,
        "activitiesCompletedCount": completed_count,
        "activitiesOverdueCount": overdue_count,
    }
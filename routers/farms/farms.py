from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from routers.farms.schemas import FarmCreate, FarmOut, UpdateFarm
from database import get_db
from models import Farm
from dependencies import verify_token
from utils import settings


router = APIRouter(prefix="/farms", tags=["farms"])

# Get farms, optionally filter by farmerId
@router.get("/", response_model=list[FarmOut])
def read_farms(farmerId: int | None = None, db: Session = Depends(get_db), farmer_id: int = Depends(verify_token), admin_key: str | None = None):
    
    # if admin_key is provided, verify it and return all farms or farms for given farmerId
    if admin_key != None:
        # verify admin key
        if admin_key != settings.ADMIN_KEY:
            raise HTTPException(status_code=401, detail="Invalid admin key")
        if farmerId != None:
            return db.query(Farm).filter(Farm.farmerId == farmerId).all()
        else:
            return db.query(Farm).all()
        
    # if no admin_key, verify farmer_id from token and return farms for that farmer only
    else:
        if not farmer_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized: Invalid Authorization token")
        # verify farmerId matches authenticated farmer_id
        if farmerId != farmer_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: You can only access your own farms")
        
        return db.query(Farm).filter(Farm.farmerId == farmerId).all()    


# create farm
@router.post("/", response_model=FarmOut, status_code=201)
def creating_a_farm(payload: FarmCreate, db: Session = Depends(get_db), farmer_id: int = Depends(verify_token)):
    if not farmer_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized: Invalid Authorization token")
    
    # check if farmerId in payload matches the authenticated farmer_id
    if payload.farmerId != farmer_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: You can only create farms for your own account")
    
    # create farm
    farm = Farm(
        farmerId=payload.farmerId,
        name=payload.name,
        sizeAcres=payload.sizeAcres,
    )

    # save to db
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm

# update farm
@router.put("/{farmId}", response_model=FarmOut)
def update_farm(farmId: int, payload: UpdateFarm, db: Session = Depends(get_db), farmer_id: int = Depends(verify_token)):
    if not farmer_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized: Invalid Authorization token")
    
    # check if farm exists
    farm = db.query(Farm).get(farmId)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
        
    # check if farm belongs to authenticated farmer
    if farm.farmerId != farmer_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: You can only update your own farms")
    
    # update fields if provided
    if payload.name is not None:
        farm.name = payload.name
    if payload.sizeAcres is not None:
        farm.sizeAcres = payload.sizeAcres
    
    # save to db
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm
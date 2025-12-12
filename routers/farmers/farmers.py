from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from routers.farmers.schemas import FarmerCreate, FarmerOut, FarmerLogin
from database import get_db
from models import Farmer
import bcrypt
from utils import settings
import jwt
from datetime import datetime, timedelta
from dependencies import nairobi_tz


router = APIRouter(prefix="/farmers", tags=["farmers"])


# Get all farmers (admin only)
@router.get("/", response_model=list[FarmerOut])
def read_farmers(db: Session = Depends(get_db), admin_key: str = Header()):
    # verify admin key
    if admin_key != settings.ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key")
    
    return db.query(Farmer).all()


# Create a new farmer (admin only)
@router.post("/", response_model=FarmerOut, status_code=status.HTTP_201_CREATED)
def create_farmer(payload: FarmerCreate, db: Session = Depends(get_db), admin_key: str = Header()):
    # verify admin key
    if admin_key != settings.ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key")
    
    # check if phoneNumber already exists
    existing_farmer = db.query(Farmer).filter(
        (Farmer.phoneNumber == payload.phoneNumber)
    ).first()
    if existing_farmer:
        raise HTTPException(status_code=400, detail="Farmer with given phone number already exists")
    
    #  check if email already exists
    existing_email = db.query(Farmer).filter(
        (Farmer.email == payload.email)
    ).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Farmer with given email already exists")
    
    # hash password
    hashed = bcrypt.hashpw(payload.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # create farmer
    farmer = Farmer(
        name=payload.name,
        phoneNumber=payload.phoneNumber,
        email=payload.email,
        hashedPassword=hashed,
    )

    # save to db
    db.add(farmer)
    db.commit()
    db.refresh(farmer)
    return farmer


# Farmer login
@router.post("/login")
def login_farmer(payload: FarmerLogin, db: Session = Depends(get_db)):
    # find farmer by phone number
    farmer = db.query(Farmer).filter(Farmer.phoneNumber == payload.phoneNumber).first()
    if not farmer:
        raise HTTPException(status_code=401, detail="Invalid phone number or password")
    
    if not bcrypt.checkpw(payload.password.encode("utf-8"), farmer.hashedPassword.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid phone number or password")
    
    # generate jwt token
    expire = datetime.now(tz=nairobi_tz) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    user = {"farmerId": farmer.id}
    to_encode = {"sub": str(farmer.id), "user": user, "exp": expire.timestamp()}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    
    return {"message": "Login successful", "farmerId": farmer.id, "jwt_access_token": encoded_jwt}
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.farmers.farmers import router as farmers_router
from routers.farms.farms import router as farms_router
from routers.seasons.seasons import router as seasons_router
from sqlalchemy.orm import Session
from database import get_db
from sqlalchemy import text


app = FastAPI(
    title="EzyAgric Backend API",
    version="0.1.0",
    description="EzyAgric Backend API created by Mujuzi Denis. For testing purposes only. admin-key: admin.123@456",
)

app.include_router(farmers_router)
app.include_router(farms_router)
app.include_router(seasons_router)

# CORS middleware. allowing all origins for now(development purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# check health of the app. currently only check if db is reachable
@app.get("/health")
async def health_check():
    try:
        db: Session = next(get_db())
        # simple query to check db connectivity
        db.execute(text("SELECT 1"))
        return {"status": "healthy"}
    except Exception as e:
        return {"status": "unhealthy", "detail": str(e)}
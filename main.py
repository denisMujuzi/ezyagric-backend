from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.farmers.farmers import router as farmers_router
from routers.farms.farms import router as farms_router
from routers.seasons.seasons import router as seasons_router


app = FastAPI()

app.include_router(farmers_router)
app.include_router(farms_router)
app.include_router(seasons_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}



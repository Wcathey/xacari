from fastapi import FastAPI
from app.routes.health import router as health_router

app = FastAPI(
    title="Xacari API",
    version="0.1.0"
)

app.include_router(health_router)

@app.get("/")
async def root():
    return {
        "message": "Xacari Backend Running"
    }

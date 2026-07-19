from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.webhooks import router
from app.api.stats import router as stats_router
from app.database import init_db

app = FastAPI(title="CodeSense", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(stats_router)

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/")
def root():
    return {"status": "CodeSense is running"}
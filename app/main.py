from fastapi import FastAPI
from app.api.webhooks import router

app = FastAPI(title="CodeSense", version="0.1.0")
app.include_router(router)

@app.get("/")
def root():
    return {"status": "CodeSense is running"}
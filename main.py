import os
from typing import Annotated
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from token_generator import generate_token_sync

API_KEY = os.getenv("API_KEY")
app = FastAPI(title="JWT API", version="1.0.0")

class JWTRequest(BaseModel):
    uid: str = Field(min_length=1, max_length=32)
    password: str = Field(min_length=1, max_length=512)

@app.get("/")
def root():
    return {"ok": True, "service": "JWT API"}

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/api/jwt")
def jwt_endpoint(body: JWTRequest, x_api_key: Annotated[str | None, Header()] = None):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    token, region, error = generate_token_sync(body.uid, body.password)
    if not token:
        raise HTTPException(status_code=401, detail=error or "Authentication failed")
    return {"success": True, "uid": body.uid, "region": region, "jwt": token}

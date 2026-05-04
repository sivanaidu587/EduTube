from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional
import os
import jwt
import secrets
import base64
from passlib.context import CryptContext

app = FastAPI()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secure Config from .env
SECRET_KEY = os.getenv('AUTH_SECRET_KEY')
if not SECRET_KEY:
    SECRET_KEY = secrets.token_urlsafe(32)
    print(f"Generated new SECRET_KEY: {SECRET_KEY}")
    print("Add AUTH_SECRET_KEY to .env for production!")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Load demo user from env (set in .env or empty)
DEMO_EMAIL = os.getenv('DEMO_EMAIL', '')
DEMO_PASS_HASH = os.getenv('DEMO_PASS_HASH', '')
DEMO_PHONE = os.getenv('DEMO_PHONE', '')

WHITELIST: Dict[str, dict] = {}
if DEMO_EMAIL and DEMO_PASS_HASH and DEMO_PHONE:
    WHITELIST[DEMO_EMAIL.lower()] = {
        "password": DEMO_PASS_HASH,
        "phone": DEMO_PHONE
    }
else:
    print("No demo user configured. Set DEMO_EMAIL, DEMO_PASS_HASH, DEMO_PHONE in .env")

class LoginRequest(BaseModel):
    identifier: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

@app.post("/login", response_model=Token)
async def login(request: LoginRequest):
    identifier = request.identifier.lower()
    
    if not WHITELIST:
        raise HTTPException(status_code=503, detail="Auth not configured. Check .env")
    
    if identifier not in WHITELIST:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user_data = WHITELIST[identifier]
    if not pwd_context.verify(request.password, user_data["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create JWT
    payload = {
        "sub": identifier,
        "phone": user_data["phone"],
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    return {"access_token": token, "token_type": "bearer"}

@app.get("/protected")
async def protected_route(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"user": payload["sub"], "phone": payload.get("phone")}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)


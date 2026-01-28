from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import jwt

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
SECRET_KEY = "sample_key"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
security = HTTPBearer()

# --------------------------------------------------
# MODELS
# --------------------------------------------------
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

# --------------------------------------------------
# FAKE DB (replace with real DB later)
# --------------------------------------------------
fake_users_db = {}

# --------------------------------------------------
# JWT FUNCTIONS
# --------------------------------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# --------------------------------------------------
# AUTH ENDPOINTS
# --------------------------------------------------
@app.post("/register", response_model=TokenResponse)
def register(user: UserRegister):
    if user.username in fake_users_db:
        raise HTTPException(status_code=400, detail="User already exists")

    fake_users_db[user.username] = user.password

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }

@app.post("/login", response_model=TokenResponse)
def login(user: UserLogin):
    if user.username not in fake_users_db or fake_users_db[user.username] != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
from pydantic import BaseModel

class CustomerData(BaseModel):
    tenure: int
    monthly_charges: float
    total_charges: float

class PredictionResponse(BaseModel):
    churn: bool
    probability: float

@app.post("/predict/auth", response_model=PredictionResponse)
def predict_churn(data: CustomerData, username: str = Depends(verify_token)):
    print(f"User {username} accessed prediction")

    # Dummy logic (replace with ML model)
    churn = data.monthly_charges > 70
    probability = 0.85 if churn else 0.15

    return {
        "churn": churn,
        "probability": probability
    }
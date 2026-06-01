from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, Token
from app.services.auth_service import auth_service
import uuid
import os
import resend
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

from dotenv import load_dotenv


router = APIRouter()
load_dotenv() # Load environment variables from .env file

# Secret key from your .env
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

resend.api_key = os.getenv("RESEND_API_KEY")
@router.post("/register")
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # 1. Check if user exists
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # 2. Hash password and create user
    hashed_pwd = auth_service.get_password_hash(user_data.password)
    

    v_token = str(uuid.uuid4()) # Unique token for email link
    
    new_user = User(
        email=user_data.email, 
        hashed_password=hashed_pwd,
        verification_token=v_token
    )
    
    db.add(new_user)
    db.commit()
    

    # 2. REAL WORLD LOGIC: Send the Email via Resend
    try:
        # Note: Resend's free tier only lets you send to your OWN registered email
        # until you add a custom domain. For testing, this is perfect!
        params = {
            "from": "MedicalAI <onboarding@resend.dev>",
            "to": [user_data.email],
            "subject": "Verify your Medical AI Account",
            "html": f"""
                <h1>Welcome to MediAI!</h1>
                <p>Thank you for joining our secure health platform.</p>
                <p>Please use the following token to verify your account:</p>
                <strong style="font-size: 20px; color: #4F46E5;">{v_token}</strong>
                <br/><br/>
                <p>Or click this link (for future frontend):</p>
                <a href="http://localhost:3000/verify-email?token={v_token}">Verify Account</a>
            """
        }
        resend.Emails.send(params)
        print(f"✅ Real Email sent successfully to {user_data.email}")

    except Exception as e:
        print(f"❌ Resend Error: {e}")
        # We don't crash the app if email fails in dev
    
    return {"message": "Registration successful. Please check your real inbox!"}

@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user or not auth_service.verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Please verify your email first")

    # Generate JWT Token
    access_token = auth_service.create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

# response_model=Token add karein taaki ye token return kar sake
@router.get("/verify-email/{token}", response_model=Token)
def verify_email(token: str, db: Session = Depends(get_db)):
    # 1. User dhoondo
    user = db.query(User).filter(User.verification_token == token).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    # 2. Activate karo
    user.is_verified = True
    user.verification_token = None
    db.commit()

    # 3. AUTO-LOGIN LOGIC: Verification ke saath hi Token de do
    access_token = auth_service.create_access_token(data={"sub": user.id})
    
    return {"access_token": access_token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme)):
    """Extracts user_id from the JWT Token."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id # This returns the REAL UUID of the logged-in user
    except JWTError:
        raise credentials_exception
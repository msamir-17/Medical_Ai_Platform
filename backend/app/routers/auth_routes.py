from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin, Token
from app.services.auth_service import auth_service
import uuid

router = APIRouter()

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
    
    # 3. Industry Logic: Yahan se ek real email jayega (Humein SMTP setup chahiye hoga)
    # Abhi ke liye hum terminal mein token print karenge
    print(f"📧 EMAIL SENT TO {user_data.email}: Verify using token {v_token}")
    
    return {"message": "Registration successful. Please check your email for verification link."}

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

@router.get("/verify-email/{token}")
def verify_email(token: str, db: Session = Depends(get_db)):
    # 1. Dhoondo ki ye token kis user ka hai
    user = db.query(User).filter(User.verification_token == token).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    
    # 2. User ko activate karo
    user.is_verified = True
    user.verification_token = None # Token delete kar do (Security best practice)
    
    db.commit()
    
    return {"message": "Email verified successfully! You can now login."}
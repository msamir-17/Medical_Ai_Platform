from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
import os

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration (industry secret keys)
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-it-later")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440 # 24 hours

class AuthService:
    def verify_password(self, plain_password: str, hashed_password: str):
        # Professional practice: Truncate to 72 before verifying too
        return pwd_context.verify(plain_password[:72], hashed_password)

    # def get_password_hash(self, password: str):
    #     """
    #     Hashes the password while ensuring it stays within bcrypt's 72-byte limit.
    #     """
    #     print("\n--- DEBUG START ---")
    #     print(f"RAW PASSWORD RECEIVED: {password}")
    #     print(f"TYPE OF PASSWORD: {type(password)}")
    #     print(f"LENGTH OF PASSWORD: {len(str(password))}")
    #     print("--- DEBUG END ---\n")
        
    #     # 3. Hash the safe version
    #     return pwd_context.hash(str(password)[:72])
    
    def get_password_hash(self, password: str):
        # We don't need the prints or the truncation anymore 
        # because bcrypt 4.0.1 will handle the string correctly.
        return pwd_context.hash(password)

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

auth_service = AuthService()
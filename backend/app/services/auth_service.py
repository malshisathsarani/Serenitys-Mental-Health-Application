"""
Authentication Service
JWT token generation, password hashing, and user authentication
"""
import logging
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from jose import JWTError, jwt
from pydantic import EmailStr

from app.core.config import settings
from app.models.database import User
from app.models.schemas import UserResponse

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for JWT and password management"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        logger.info("Initializing Auth Service")
        self._initialized = True
    
    # ========================================================================
    # PASSWORD HASHING & VERIFICATION
    # ========================================================================
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using PBKDF2 (more compatible than bcrypt)"""
        try:
            # Generate random salt
            salt = secrets.token_hex(32)
            # Hash password with PBKDF2
            hashed = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode(),
                salt.encode(),
                100000  # iterations
            ).hex()
            # Return salt:hash format
            return f"{salt}:{hashed}"
        except Exception as e:
            logger.error(f"[HASH] Password hashing failed: {type(e).__name__}: {e}")
            raise
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        try:
            salt, hashed = hashed_password.split(':')
            plain_hashed = hashlib.pbkdf2_hmac(
                'sha256',
                plain_password.encode(),
                salt.encode(),
                100000
            ).hex()
            return plain_hashed == hashed
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    # ========================================================================
    # JWT TOKEN GENERATION & VALIDATION
    # ========================================================================
    
    def create_access_token(self, user_id: int, email: str, expires_delta: Optional[timedelta] = None) -> Dict[str, any]:
        """
        Create a JWT access token
        
        Returns dict with token, token_type, and expires_in
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        expire = datetime.utcnow() + expires_delta
        to_encode = {
            "user_id": user_id,
            "email": email,
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        logger.info(f"Access token created for user_id={user_id}")
        
        return {
            "access_token": encoded_jwt,
            "token_type": "bearer",
            "expires_in": int(expires_delta.total_seconds())
        }
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify and decode a JWT token
        
        Returns token payload or None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError as e:
            logger.error(f"Token validation error: {e}")
            return None
    
    # ========================================================================
    # USER REGISTRATION & LOGIN
    # ========================================================================
    
    async def register_user(
        self,
        username: str,
        email: EmailStr,
        password: str,
        full_name: Optional[str],
        db: AsyncSession
    ) -> Dict:
        """
        Register a new user
        
        Returns user info or error dict
        """
        try:
            # Check if user already exists
            result = await db.execute(
                select(User).where(
                    (User.email == email) | (User.username == username)
                )
            )
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                if existing_user.email == email:
                    return {
                        "status": "error",
                        "error": "Email already registered"
                    }
                return {
                    "status": "error",
                    "error": "Username already taken"
                }
            
            # Create new user
            logger.info(f"[REGISTER] Hashing password for user {username}")
            hashed_password = self.hash_password(password)
            logger.info(f"[REGISTER] Password hashed successfully, creating user object")
            new_user = User(
                username=username.lower(),
                email=email.lower(),
                password_hash=hashed_password,
                full_name=full_name,
                is_active=True,
                is_verified=False  # Email verification feature
            )
            
            logger.info(f"[REGISTER] Adding user to database")
            db.add(new_user)
            await db.flush()
            await db.commit()
            
            logger.info(f"New user registered: {username} ({email})")
            
            # Generate token
            token_data = self.create_access_token(new_user.id, new_user.email)
            
            return {
                "status": "success",
                "user": UserResponse.from_orm(new_user),
                "access_token": token_data["access_token"],
                "token_type": token_data["token_type"],
                "expires_in": token_data["expires_in"]
            }
            
        except Exception as e:
            logger.error(f"Registration error: {e}", exc_info=True)
            await db.rollback()
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def login_user(
        self,
        email: EmailStr,
        password: str,
        db: AsyncSession
    ) -> Dict:
        """
        Authenticate user and generate token
        
        Returns token or error dict
        """
        try:
            # Find user by email
            result = await db.execute(
                select(User).where(User.email == email.lower())
            )
            user = result.scalar_one_or_none()
            
            if not user or not self.verify_password(password, user.password_hash):
                logger.warning(f"Failed login attempt for email: {email}")
                return {
                    "status": "error",
                    "error": "Invalid email or password"
                }
            
            if not user.is_active:
                logger.warning(f"Login attempt for inactive user: {email}")
                return {
                    "status": "error",
                    "error": "Account is inactive"
                }
            
            # Update last login
            user.last_login_at = datetime.utcnow()
            await db.commit()
            
            # Generate token
            token_data = self.create_access_token(user.id, user.email)
            
            logger.info(f"User logged in: {email}")
            
            return {
                "status": "success",
                "user": UserResponse.from_orm(user),
                "access_token": token_data["access_token"],
                "token_type": token_data["token_type"],
                "expires_in": token_data["expires_in"]
            }
            
        except Exception as e:
            logger.error(f"Login error: {e}", exc_info=True)
            return {
                "status": "error",
                "error": "Authentication failed"
            }
    
    # ========================================================================
    # USER LOOKUP & VERIFICATION
    # ========================================================================
    
    async def get_user_by_id(self, user_id: int, db: AsyncSession) -> Optional[User]:
        """Get user by ID"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str, db: AsyncSession) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()
    
    # ========================================================================
    # PASSWORD MANAGEMENT
    # ========================================================================
    
    async def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str,
        db: AsyncSession
    ) -> Dict:
        """Change user password"""
        try:
            user = await self.get_user_by_id(user_id, db)
            
            if not user:
                return {"status": "error", "error": "User not found"}
            
            if not self.verify_password(old_password, user.password_hash):
                return {"status": "error", "error": "Incorrect current password"}
            
            if old_password == new_password:
                return {"status": "error", "error": "New password must be different"}
            
            user.password_hash = self.hash_password(new_password)
            await db.commit()
            
            logger.info(f"Password changed for user_id={user_id}")
            return {"status": "success", "message": "Password updated successfully"}
            
        except Exception as e:
            logger.error(f"Password change error: {e}")
            await db.rollback()
            return {"status": "error", "error": str(e)}


def get_auth_service() -> AuthService:
    """FastAPI dependency for auth service"""
    return AuthService()

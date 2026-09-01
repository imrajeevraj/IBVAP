from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import time
import logging
import redis

from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.core.security import create_access_token, get_current_user, verify_password
from backend.app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

logger = logging.getLogger("Auth")

redis_client = None
try:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
except Exception as e:
    logger.warning(f"Could not connect to Redis: {e}")

MAX_ATTEMPTS = 5
LOCKOUT_WINDOW = 60  # seconds

@router.post("/login")
def login(request: Request, response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    
    if redis_client:
        try:
            key = f"rate_limit:login:{client_ip}"
            current_time = time.time()
            
            # Use a Redis sorted set for sliding window rate limiting
            redis_client.zremrangebyscore(key, 0, current_time - LOCKOUT_WINDOW)
            attempts = redis_client.zcard(key)
            
            if attempts >= MAX_ATTEMPTS:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many login attempts. Please try again later.",
                )
        except redis.RedisError as e:
            logger.error(f"Redis error during rate limiting: {e}")
    
    user = db.query(User).filter(User.username == form_data.username).first()
    if user is None or not verify_password(form_data.password, user.hashed_password):
        if redis_client:
            try:
                redis_client.zadd(key, {str(current_time): current_time})
                redis_client.expire(key, LOCKOUT_WINDOW)
            except redis.RedisError:
                pass
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user.username, user.role)
    response.set_cookie(
        key="ibvap_access_token",
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=60 * 60 * 8,
    )
    return {
        "token_type": "bearer",
        "username": user.username,
        "role": user.role,
    }


@router.get("/me")
def get_me(user: User = Depends(get_current_user)):
    return {"username": user.username, "role": user.role}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    response.delete_cookie("ibvap_access_token")

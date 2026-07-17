from uuid import UUID
from fastapi import Depends, HTTPException, status
from typing import Annotated
from datetime import datetime,timedelta, timezone
from sqlalchemy import select

from app.core.settings import settings

from passlib.context import CryptContext

from sqlalchemy.ext.asyncio  import AsyncSession
from app.db.dependancy import get_db
from app.models.model import User
from fastapi.security import OAuth2PasswordBearer

from jose import JWTError, jwt

db_dependency= Annotated[AsyncSession,Depends(get_db)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

passlib_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def authenticate_user(email: str, password: str,db:db_dependency):
    #check if email exists
    result= await db.execute(select(User).where(User.email==email))
    user=result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    #verify password
    if not passlib_context.verify(password,user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return user

def create_acess_token(email: str, user_id: UUID, role: str, expires_delta: timedelta | None = None):
    to_encode = {"sub": str(user_id), "email": email, "role": role}
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode,settings.SECRET_KEY,algorithm=settings.ALGORITHM)


def create_refresh_token(user_id: UUID, expires_delta: timedelta | None = None):
    to_encode = {"sub": str(user_id),"type": "refresh"}
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode,settings.SECRET_KEY,algorithm=settings.ALGORITHM)
    

def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_user(
    db: db_dependency,
    token: Annotated[str, Depends(oauth2_scheme)],
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user_id = UUID(user_id)

        result = await db.execute(
            select(User).where(
                User.id == user_id
            )
        )

        user = result.scalar_one_or_none()

        if not user:
            raise credentials_exception

        return user

    except (JWTError, ValueError):
        raise credentials_exception
     
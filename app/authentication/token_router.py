from sqlalchemy import select
from datetime import timedelta
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from .auth import authenticate_user

from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependancy import get_db

from app.authentication.auth import create_acess_token, create_refresh_token, verify_refresh_token
from app.core.settings import settings

from app.schemas.user_schemas import Token, RefreshToken as RefreshTokenSchema
from app.models.model import RefreshToken

from datetime import datetime, timezone
from uuid import UUID

# from passlib.context import CryptContext

router = APIRouter(
    prefix="/auth",
    tags=['authentication']
)

db_dependency = Annotated[AsyncSession, Depends(get_db)]
# passlib_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post('/login')
async def login_for_acess_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db:db_dependency):
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    email = form_data.username
    user_id = user.id
    role = user.role

    access_token = create_acess_token(email,user_id,role,expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_refresh_token(user_id,expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))

    db_refresh_token = RefreshToken(
        user_id=user_id,
        token=refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        revoked=False,
    )
    db.add(db_refresh_token)
    await db.commit()
    await db.refresh(db_refresh_token)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
    )

@router.post('/token/refresh')
async def refresh_acess_token(token: RefreshTokenSchema, db:db_dependency):
    payload = verify_refresh_token(token.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    user_id = UUID(payload.get("sub"))
    email = payload.get("email")
    role = payload.get("role")

    result = await db.execute(select(RefreshToken).where(RefreshToken.token == token.refresh_token))
    db_refresh_token = result.scalar_one_or_none()

    if not db_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    if db_refresh_token.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    
    db_refresh_token.revoked = True
    db.add(db_refresh_token)
    await db.commit()
    await db.refresh(db_refresh_token)
    
    access_token = create_acess_token(email,user_id,role,expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_refresh_token(user_id,expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))

    new_db_refresh_token = RefreshToken(
        user_id=user_id,
        token=refresh_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        revoked=False,
    )
    db.add(new_db_refresh_token)
    await db.commit()
    await db.refresh(new_db_refresh_token)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
    )


@router.post('/logout')
async def logout(token: RefreshTokenSchema, db: db_dependency):

    verify_refresh_token(token.refresh_token)
    result = await db.execute(select(RefreshToken).where(RefreshToken.token == token.refresh_token))
    db_refresh_token = result.scalar_one_or_none()

    if not db_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check whether it is already revoked
    if db_refresh_token.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token already revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Mark the token as revoked
    db_refresh_token.revoked = True
    await db.commit()

    return {
        'message': 'Logged out successfully'
    }
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException, Body, Query, Response, Request, Cookie
from sqlalchemy.ext.asyncio.session import AsyncSession
from itsdangerous import SignatureExpired, BadSignature
from jose import jwt, ExpiredSignatureError, JWTError

from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_user_email, get_email_token_serializer, verify_password, create_access_token, \
    create_refresh_token
from app.crud.user import get_user_by_email, create_user, get_user_by_id
from app.schemas.auth import TokenResponse, LoginRequest, TokenRefreshRequest
from app.schemas.user import UserOut, UserCreate

router = APIRouter(prefix="/auth", tags=["auth", "users"])


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
        user_in: Annotated[UserCreate, Body()],
        db: Annotated[AsyncSession, Depends(get_db)],
):
    existing = await get_user_by_email(user_in.email, db)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = await create_user(db, user_in)

    return user


@router.get("/verify-email/",
            response_model=dict,
            status_code=status.HTTP_200_OK,
            summary="Verify user email address",
            description="Verifies user email address")
async def verify_email(
        token: Annotated[str, Query(..., description="Email verification token")],
        db: Annotated[AsyncSession, Depends(get_db)]
):
    # email = verify_user_email(token)
    serializer = get_email_token_serializer()
    try:
        email = serializer.loads(token, max_age=3600 * 24)
    except SignatureExpired:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired")
    except BadSignature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

    user = await get_user_by_email(email, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if user.is_verified:
        return {"message": "User is verified"}

    user.is_verified = True
    user.is_active = True

    await db.commit()

    return {"message": "Email verified"}


@router.post("/login", response_model=TokenResponse)
async def login(
        login_in: Annotated[LoginRequest, Body()],
        db: Annotated[AsyncSession, Depends(get_db)],
        response: Response
):
    user = await get_user_by_email(login_in.email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    if not user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not verified")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not active")

    # TODO: handle support bruteforce login
    if not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    access_token = create_access_token(str(user.id), [user.role.value])
    new_refresh_token = create_refresh_token(str(user.id))

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        max_age=60 * 60 * 24 * settings.REFRESH_TOKEN_EXPIRE_DAYS,
        secure=True,
        samesite="lax",
        path="/",
    )
    return {"access_token": access_token, "refresh_token": new_refresh_token}


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="obtain new access token using valid refresh token"
)
async def refresh_token(
        request: Request,
        response: Response,
        db: Annotated[AsyncSession, Depends(get_db)],
        refresh_token_cookie: Annotated[str | None, Cookie()] = None,
        body: TokenRefreshRequest | None = None
):
    token = (
            (body.refresh_token if body and body.refresh_token else None)
            or refresh_token_cookie
            or request.cookies.get("refresh_token")
    )
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing refresh token")

    try:
        payload = jwt.decode(
            token=token,
            key=settings.JWT_PUBLIC_KEY_PEM,
            algorithms=[settings.JWT_ALGORITHM]
        )
        token_type = payload.get("token_type")
        if token_type != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token payload")

    user = await get_user_by_id(int(user_id), db)
    if not user or not user.is_verified or not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is not active or not verified")

    access_token = create_access_token(subject=str(user.id), roles=[user.role.value])
    new_refresh_token = create_refresh_token(subject=str(user.id))

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        max_age=60 * 60 * 24 * settings.REFRESH_TOKEN_EXPIRE_DAYS,
        secure=True,
        samesite="lax",
        path="/",
    )
    return {"access_token": access_token, "refresh_token": new_refresh_token}

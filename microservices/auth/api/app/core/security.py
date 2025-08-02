import datetime as dt
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from itsdangerous import URLSafeTimedSerializer
from app.core.config import settings
from pydantic import EmailStr


pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_password_hash(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a hashed password against one provided by the user."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str, roles: list[str]) -> str:
    """Generuje access token JWT podpisany RSA."""
    expire = dt.datetime.now() + dt.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": dt.datetime.now(dt.UTC),
        "roles": roles
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_PRIVATE_KEY_PEM,
        algorithm="RS256"
    )
    return encoded_jwt


def create_refresh_token(subject: str) -> str:
    """Generuje refresh token JWT podpisany RSA."""
    expire = dt.datetime.now(dt.UTC) + dt.timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "iat": dt.datetime.now(dt.UTC),
        "token_type": "refresh"
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_PRIVATE_KEY_PEM,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Dekoduje i weryfikuje JWT z podpisem RSA."""
    return jwt.decode(
        token,
        settings.JWT_PUBLIC_KEY_PEM,
        algorithms=[settings.JWT_ALGORITHM],
    )

def get_email_token_serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(settings.SECRET_KEY, salt=settings.SALT_EMAIL)

def generate_email_verification_token(email: EmailStr) -> str:
    serializer = get_email_token_serializer()
    return serializer.dumps(email)

def verify_user_email(token: str) -> EmailStr | None:
    serializer = get_email_token_serializer()
    serializer.loads(token)

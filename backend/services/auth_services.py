from datetime import datetime,timedelta,timezone
import jwt
from pwdlib import PasswordHash
from fastapi import HTTPException,status
from backend.core.config import settings

password_hash = PasswordHash.recommended()


def hash_password(password:str)->str:
    return password_hash.hash(password)

def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    if not isinstance(hashed_password, str):
        raise ValueError(
            f"Expected a password hash string, got {type(hashed_password).__name__}"
        )

    return password_hash.verify(plain_password, hashed_password)


def create_access_token(user_id:int)->str:
    expire_at = datetime.now(timezone.utc) + timedelta(
        minutes= settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub":str(user_id),
        "exp":expire_at,
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm =settings.JWT_ALGORITHM,
    )


    return token
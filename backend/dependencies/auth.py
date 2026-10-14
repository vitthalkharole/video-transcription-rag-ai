
import jwt

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.database.connection import get_db
from backend.models.user_model import User

oauth2_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired access token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )

        user_id = payload.get("sub")

        if user_id is None:
            print("DEBUG: JWT is missing the sub claim")
            raise credentials_exception

        user_id = int(user_id)

    except jwt.ExpiredSignatureError:
        print("DEBUG: Token has expired")
        raise credentials_exception

    except jwt.InvalidTokenError as exc:
        print("DEBUG: JWT validation failed:", type(exc).__name__)
        raise credentials_exception

    except (ValueError, TypeError) as exc:
        print("DEBUG: Invalid user ID in token:", type(exc).__name__)
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        print("DEBUG: No database user found for user ID:", user_id)
        raise credentials_exception

    return user

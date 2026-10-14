from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session


from backend.database.connection import get_db
from backend.models.user_model import User
from backend.schemas.auth_schema import(
    UserLoginRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,

)
from backend.services.auth_services import (
    hash_password,
    verify_password,
    create_access_token,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]

)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,

)

def register_user(
    request:UserLoginRequest,
    db:Session = Depends(get_db),
):
    
    existing_user=(
        db.query(User)
        .filter((
            User.username == request.username)|
            (User.email == request.email)
        ).first()
    )

    if existing_user :
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail = "Username or email already registered",
        )

    user =User(
        username=request.username,
        email = request.email,
        hashed_password = hash_password(request.password),

    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user



@router.post("/login", response_model=TokenResponse)
def login_user(
    request: UserLoginRequest,
    db: Session = Depends(get_db)
):
    user = (
        db.query(User)
        .filter(User.username == request.username)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )

    if not user.hashed_password:
        raise HTTPException(
            status_code=500,
            detail="Stored password hash is missing"
        )

    if not verify_password(
        request.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from core.security import verify_password, create_access_token
from models.auth import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Standard OAuth2 Login.
    username field = email
    password field = password
    """
    # 1. Find User
    user = await User.find_one(User.email == form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # 2. Check Password
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # 3. Generate Token
    # We embed the User's System Role in the token if we want, 
    # but looking it up via get_current_user is safer.
    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}

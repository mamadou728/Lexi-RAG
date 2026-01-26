from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from core.security import get_current_user, verify_password, create_access_token
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

@router.post("/logout")
async def logout():
    """
    Dummy logout endpoint.
    In a real-world scenario, you might blacklist the token or handle it client-side.
    """
    return {"message": "Logout successful"} 

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user info.
    """
    return current_user
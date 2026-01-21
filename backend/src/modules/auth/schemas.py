from pydantic import BaseModel, EmailStr, Field, validator

# 1. Schema for User Registration (Input)
class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8, description="Must be at least 8 characters")

    # Optional: basic password strength check
    @validator('password')
    def validate_password_strength(cls, v):
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one number')
        return v

# 2. Schema for User Login (Input)
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# 3. Schema for the Token Response (Output)
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    prenom: str = Field(min_length=2, max_length=50)
    wilaya: str | None = None
    filiere: str = Field(default="Sciences Expérimentales")

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):
        if v.isdigit():
            raise ValueError("Le mot de passe ne peut pas être que des chiffres")
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Le mot de passe ne peut pas dépasser 72 octets avec bcrypt")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str | None = None
    token_type: str = "bearer"
    user: dict[str, Any]


class WaitlistRequest(BaseModel):
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    wilaya: str | None = None
    lang: str = "fr"
    source: str | None = None

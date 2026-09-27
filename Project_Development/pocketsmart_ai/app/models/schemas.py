from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class HomeRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    room_type: str = Field(min_length=2, max_length=80)
    style: str = Field(default="modern", max_length=80)
    items: list[str] = Field(default_factory=list, max_length=30)
    quantities: dict[str, int] = Field(default_factory=dict)
    notes: str = Field(default="", max_length=1000)

class PartyRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    guests: int = Field(gt=0, le=10000)
    event_type: str = Field(min_length=2, max_length=80)
    venue: str = Field(default="home", max_length=120)
    city: str = Field(default="", max_length=120)
    food_preference: str = Field(default="mixed", max_length=120)
    notes: str = Field(default="", max_length=1000)

class JewelryRequest(BaseModel):
    budget: float = Field(gt=0, le=10_000_000)
    occasion: str = Field(min_length=2, max_length=80)
    style: str = Field(default="elegant", max_length=80)
    outfit_color: str = Field(default="", max_length=80)
    metal_preference: str = Field(default="any", max_length=80)
    notes: str = Field(default="", max_length=1000)

class RecommendationItem(BaseModel):
    name: str
    category: str
    estimated_price: float = Field(ge=0)
    platform: str
    url: str
    why_it_fits: str
    quantity: int = Field(default=1, ge=1)

class BudgetAllocation(BaseModel):
    category: str
    amount: float = Field(ge=0)
    percentage: float = Field(ge=0, le=100)

class RecommendationResponse(BaseModel):
    title: str
    summary: str
    total_estimated_cost: float = Field(ge=0)
    budget_remaining: float
    allocations: list[BudgetAllocation]
    recommendations: list[RecommendationItem]
    tips: list[str]
    source: Literal["gemini", "fallback"]

class RecommendationOut(BaseModel):
    id: int
    planner_type: str
    request_data: dict
    result_data: dict
    created_at: str

class SessionInfo(BaseModel):
    logged_in: bool
    user_id: int | None = None
    email: str | None = None

class SessionData(BaseModel):
    user: dict
    recent_recommendations: list[dict]

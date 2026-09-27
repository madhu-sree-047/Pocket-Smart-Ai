from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models.db import Recommendation, User
from app.models.schemas import HomeRequest, PartyRequest, JewelryRequest, RecommendationResponse
from app.services.gemini import GeminiService

router=APIRouter(tags=["planners"])
service=GeminiService()
ALLOWED={"image/jpeg","image/png","image/webp"}

def save_result(db,user,planner,request_data,result):
    rec=Recommendation(user_id=user.id,planner_type=planner,request_data=request_data,result_data=result.model_dump())
    db.add(rec); db.commit(); db.refresh(rec); return rec

@router.post("/generate-home", response_model=RecommendationResponse)
def generate_home(payload: HomeRequest, user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    result=service.home(payload); save_result(db,user,"home",payload.model_dump(),result); return result

@router.post("/generate-party", response_model=RecommendationResponse)
def generate_party(payload: PartyRequest, user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    result=service.party(payload); save_result(db,user,"party",payload.model_dump(),result); return result

@router.post("/generate-jewelry", response_model=RecommendationResponse)
async def generate_jewelry(
    budget: float = Form(...), occasion: str = Form(...), style: str = Form("elegant"), outfit_color: str = Form(""), metal_preference: str = Form("any"), notes: str = Form(""),
    outfit_image: UploadFile|None=File(default=None), user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    payload = JewelryRequest(budget=budget, occasion=occasion, style=style, outfit_color=outfit_color, metal_preference=metal_preference, notes=notes)
    image=None
    if outfit_image:
        if outfit_image.content_type not in ALLOWED: raise HTTPException(400,"Only JPG, PNG and WEBP images are allowed")
        data=await outfit_image.read()
        if len(data)>get_settings().max_upload_mb*1024*1024: raise HTTPException(413,"Image is too large")
        image=(data,outfit_image.content_type)
    result=service.jewelry(payload,image); save_result(db,user,"jewelry",payload.model_dump(),result); return result

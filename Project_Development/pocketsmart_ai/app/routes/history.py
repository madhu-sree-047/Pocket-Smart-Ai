from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.db import Recommendation, User
from app.models.schemas import RecommendationOut, SessionData

router=APIRouter(tags=["history"])

@router.get("/history", response_model=list[RecommendationOut])
def history(user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    rows=db.scalars(select(Recommendation).where(Recommendation.user_id==user.id).order_by(Recommendation.created_at.desc()).limit(50)).all()
    return [RecommendationOut(id=r.id,planner_type=r.planner_type,request_data=r.request_data,result_data=r.result_data,created_at=r.created_at.isoformat()) for r in rows]

@router.get("/recommendations-details/{recommendation_id}", response_model=RecommendationOut)
def details(recommendation_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    r=db.scalar(select(Recommendation).where(Recommendation.id==recommendation_id,Recommendation.user_id==user.id))
    if not r: raise HTTPException(404,"Recommendation not found")
    return RecommendationOut(id=r.id,planner_type=r.planner_type,request_data=r.request_data,result_data=r.result_data,created_at=r.created_at.isoformat())

@router.get("/session-data", response_model=SessionData)
def session_data(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    rows=db.scalars(select(Recommendation).where(Recommendation.user_id==user.id).order_by(Recommendation.created_at.desc()).limit(5)).all()
    return SessionData(user={"id":user.id,"name":user.name,"email":user.email},recent_recommendations=[{"id":r.id,"planner_type":r.planner_type,"created_at":r.created_at.isoformat()} for r in rows])

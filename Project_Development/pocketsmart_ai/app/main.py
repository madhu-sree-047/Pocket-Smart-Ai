from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from app.database import Base, engine
from app.routes import auth, planners, history, pages

@asynccontextmanager
async def lifespan(app:FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

settings=get_settings()
app=FastAPI(title=settings.app_name,version="1.0.0",description="Budget-aware generative AI recommendation assistant",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origin_list,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.mount("/static",StaticFiles(directory="app/static"),name="static")
app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(planners.router)
app.include_router(history.router)

@app.get("/health",tags=["system"])
def health(): return {"status":"ok","app":settings.app_name}

from fastapi import APIRouter
from services.content_gen import generate_daily_posts
from models.schema import ContentRequest
from dotenv import load_dotenv

load_dotenv()
posts_router = APIRouter()

@posts_router.post("/generate")
async def generate_posts(req: ContentRequest):
    return await generate_daily_posts(req.topic,req.method, req.days)
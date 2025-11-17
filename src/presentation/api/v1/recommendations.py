from fastapi import APIRouter

from src.main import recommender

recommendations_router = APIRouter(prefix="/recommendations")


@recommendations_router.get("/{user_id}")
async def get_recommendations(user_id: int, top_n: int = 10):
    return await recommender.recommend_for_user(user_id, top_n)

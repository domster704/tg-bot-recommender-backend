from src.domain.entities.movie_lens.raitings import Rating
from src.domain.interfaces.recommender import IRecommender


class UpdateRecommenderUseCase:
    def __init__(self, recommender: IRecommender):
        self.recommender = recommender

    async def execute(self, rating: Rating) -> None:
        await self.recommender.update_for_rating(rating)

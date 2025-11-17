from fastapi import Depends

from src.application.providers.uow import uow_provider
from src.application.usecase.recommender.recommender_builder import RecommenderBuilderUseCase
from src.domain.services.recommender.item_based_cf_recommender import ItemBasedCFRecommender
from src.infrastructure.repositories.movie import MovieRepository
from src.infrastructure.repositories.rating import RatingRepository


def recommender_builder(uow=Depends(uow_provider)) -> RecommenderBuilderUseCase:
    rating_repository = RatingRepository(uow)
    movie_repository = MovieRepository(uow)

    return RecommenderBuilderUseCase(
        rating_repository=rating_repository,
        movie_repository=movie_repository,
        recommender=ItemBasedCFRecommender()
    )

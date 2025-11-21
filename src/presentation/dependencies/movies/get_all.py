from fastapi.params import Depends

from src.application.providers.uow import uow_provider
from src.application.usecase.movies.get_all import MoviesGetAllUseCase
from src.infrastructure.repositories.movie import MovieRepository


def get_all_movies_use_case(uow=Depends(uow_provider)) -> MoviesGetAllUseCase:
    return MoviesGetAllUseCase(movie_repository=MovieRepository(uow))

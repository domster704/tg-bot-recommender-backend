from src.domain.entities.movie_lens.movie import Movie
from src.domain.repositories.base import RepositoryInterface


class MoviesGetAllUseCase:
    def __init__(self, movie_repository: RepositoryInterface[Movie]):
        self.movie_repository = movie_repository

    async def execute(self) -> list[Movie]:
        movies: list[Movie] = await self.movie_repository.get_all()
        return movies

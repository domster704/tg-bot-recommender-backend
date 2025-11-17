from typing import Protocol

from src.domain.entities.movie_lens.movie import Movie
from src.domain.entities.movie_lens.raitings import Rating


class IRecommender(Protocol):
    async def build(self, ratings: list[Rating], movies: list[Movie]) -> None:
        """
        Формирует внутреннюю модель рекомендаций на основе переданных данных

        Args:
            ratings: Список всех пользовательских оценок
            movies: Список всех фильмов, для которых нужно построить модель

        Returns:
            None
        """
        ...

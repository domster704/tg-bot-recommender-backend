from collections import defaultdict
from math import sqrt
from typing import Callable, Awaitable

from src.domain.entities.movie_lens.movie import Movie
from src.domain.entities.movie_lens.raitings import Rating
from src.domain.interfaces.recommender import IRecommender
from src.domain.interfaces.similarity_cache import ISimilarityCache


class ItemBasedCFRecommender(IRecommender):
    """
    Рекомендательная система на основе item-based collaborative filtering.

    Хранит матрицу схожести фильмов и структуру оценок пользователей
    """

    def __init__(self, cache: ISimilarityCache | None = None):
        self.cache = cache

        # Матрица схожести фильмов
        # movie1.id -> movie2.id -> cos-similarity
        self.similarity_matrix: dict[int, dict[int, float]] = defaultdict(dict)

        # Все оценки пользователей
        # user.id -> movie.id -> rating
        self.user_ratings: dict[int, dict[int, int]] = defaultdict(dict)

    async def build(
        self,
        ratings_loader: Callable[[], Awaitable[list[Rating]]],
        movies_loader: Callable[[], Awaitable[list[Movie]]],
    ) -> None:
        if self.cache:
            matrix = await self.cache.load()
            if matrix:
                self.similarity_matrix = matrix
                return

        ratings = await ratings_loader()
        movies = await movies_loader()

        print("Загружено рейтингов:", len(ratings))

        self._fill_user_ratings(ratings)
        self._build_similarity_matrix(movies)

        print("Матрица сходства фильмов построена")

        if self.cache:
            await self.cache.save(self.similarity_matrix)

    def _fill_user_ratings(self, ratings: list[Rating]) -> None:
        for rating in ratings:
            self.user_ratings[rating.user.id][rating.movie.id] = rating.rating

    def _build_similarity_matrix(self, movies: list[Movie]) -> None:
        """
        Строит матрицу косинусных сходств между всеми парами фильмов

        Args:
            movies: Список всех фильмов из базы данных
        """
        movie_vectors: dict[int, dict[int, int]] = defaultdict(dict)

        for user, movie_data in self.user_ratings.items():
            for movie_id, rating in movie_data.items():
                movie_vectors[movie_id][user] = rating

        movie_ids: list[int] = [m.id for m in movies]

        for i, movie1 in enumerate(movie_ids):
            movie1_vector: dict[int, int] = movie_vectors.get(movie1, {})

            for movie2 in movie_ids[i + 1 :]:
                movie2_vector: dict[int, int] = movie_vectors.get(movie2, {})
                similarity: float = self._cosine(movie1_vector, movie2_vector)

                if similarity > 0:
                    self.similarity_matrix[movie1][movie2] = similarity
                    self.similarity_matrix[movie2][movie1] = similarity

    @staticmethod
    def _cosine(vector1: dict[int, int], vector2: dict[int, int]) -> float:
        """
        Вычисляет косинусное сходство двух векторов рейтингов

        Args:
            vector1: Словарь рейтингов первого фильма, вида user_id → rating
            vector2: Словарь рейтингов второго фильма

        Returns:
            Значение косинусного сходства от 0 до 1
        """
        users = set(vector1) & set(vector2)
        if not users:
            return 0

        dot: float = sum(vector1[u] * vector2[u] for u in users)
        norm1: float = sqrt(sum(v * v for v in vector1.values()))
        norm2: float = sqrt(sum(v * v for v in vector2.values()))

        if norm1 == 0 or norm2 == 0:
            return 0

        return dot / (norm1 * norm2)

    def _get_movie_vector(self, movie_id: int) -> dict[int, int]:
        """
        Возвращает вектор фильма в формате:
            user_id -> rating

        Args:
            movie_id (int): ID фильма

        Returns:
            dict[int, int]: словарь вида {user_id: rating}
        """
        vector: dict[int, int] = {}
        for user_id, ratings_by_movie in self.user_ratings.items():
            if movie_id in ratings_by_movie:
                vector[user_id] = ratings_by_movie[movie_id]
        return vector

    async def recommend_for_user(self, user_id: int, top_n: int = 10) -> list[int]:
        if user_id not in self.user_ratings:
            return []

        user_movies = self.user_ratings[user_id]

        scores: dict[int, float] = defaultdict(float)
        weights: dict[int, float] = defaultdict(float)

        for movie_id, rating in user_movies.items():
            for similar_movie, sim in self.similarity_matrix[movie_id].items():
                if similar_movie in user_movies:
                    continue

                scores[similar_movie] += sim * rating
                weights[similar_movie] += abs(sim)

        recommendations: list[tuple[int, float]] = [
            (movie_id, scores[movie_id] / weights[movie_id])
            for movie_id in scores
            if weights[movie_id] > 0
        ]

        recommendations.sort(key=lambda x: x[1], reverse=True)
        recommended_movie_ids: list[int] = [
            movie_id for movie_id, _ in recommendations[:top_n]
        ]
        return recommended_movie_ids

    async def update_for_rating(self, rating: Rating) -> None:
        user_id: int = rating.user.id
        movie_id: int = rating.movie.id
        value: int = rating.rating

        self.user_ratings[user_id][movie_id] = value

        # Все фильмы, кроме текущего, которые уже оценивал пользователь
        other_movies: dict[int, int] = {
            movie_id_: r
            for movie_id_, r in self.user_ratings[user_id].items()
            if movie_id_ != movie_id
        }

        # Пересчитываем косинусное сходство только для пар:
        for other_movie_id in other_movies.keys():
            vector1: dict[int, int] = self._get_movie_vector(movie_id)
            vector2: dict[int, int] = self._get_movie_vector(other_movie_id)

            similarity: float = self._cosine(vector1, vector2)

            if similarity > 0:
                self.similarity_matrix[movie_id][other_movie_id] = similarity
                self.similarity_matrix[other_movie_id][movie_id] = similarity
            else:
                # Если сходство стало 0 - удаляем связь
                self.similarity_matrix[movie_id].pop(other_movie_id, None)
                self.similarity_matrix[other_movie_id].pop(movie_id, None)

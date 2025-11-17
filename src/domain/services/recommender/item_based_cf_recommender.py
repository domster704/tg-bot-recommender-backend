from collections import defaultdict
from math import sqrt

from src.domain.entities.movie_lens.movie import Movie
from src.domain.entities.movie_lens.raitings import Rating
from src.domain.interfaces.recommender import IRecommender


class ItemBasedCFRecommender(IRecommender):
    """
    Рекомендательная система на основе item-based collaborative filtering.

    Хранит матрицу схожести фильмов и структуру оценок пользователей
    """

    def __init__(self):
        # Матрица схожести фильмов
        # movie1.id -> movie2.id -> cos-similarity
        self.similarity_matrix: dict[int, dict[int, float]] = defaultdict(dict)

        # Все оценки пользователей
        # user.id -> movie.id -> rating
        self.user_ratings: dict[int, dict[int, int]] = defaultdict(dict)

    async def build(self, ratings: list[Rating], movies: list[Movie]) -> None:
        print("Загружено рейтингов:", len(ratings))

        for rating in ratings:
            self.user_ratings[rating.user.id][rating.movie.id] = rating.rating

        self._build_similarity_matrix(movies)

        print("Матрица сходства фильмов построена")

    def _build_similarity_matrix(self, movies: list[Movie]) -> None:
        """
        Строит матрицу косинусных сходств между всеми парами фильмов

        Args:
            movies: Список всех фильмов из базы данных
        """
        movie_vectors: dict[int, dict[int, int]] = {}

        for user, movie_data in self.user_ratings.items():
            for movie_id, rating in movie_data.items():
                movie_vectors[movie_id][user] = rating

        movie_ids: list[int] = [m.id for m in movies]

        for i, movie1 in enumerate(movie_ids):
            movie1_vector: dict[int, int] = movie_vectors.get(movie1, {})

            for movie2 in movie_ids[i + 1:]:
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

    async def recommend_for_user(self, user_id: int, top_n: int = 10) -> list[int]:
        """
        Формирует рекомендации для пользователя

        Args:
            user_id: Идентификатор пользователя
            top_n: Количество фильмов, которые нужно вернуть

        Returns:
            Список идентификаторов фильмов, рекомендованных пользователю
        """
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
            (mid, scores[mid] / weights[mid]) for mid in scores if weights[mid] > 0
        ]

        recommendations.sort(key=lambda x: x[1], reverse=True)
        recommended_movie_ids: list[int] = [
            movie_id for movie_id, _ in recommendations[:top_n]
        ]
        return recommended_movie_ids

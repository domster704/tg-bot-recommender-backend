import pickle
from pathlib import Path

from src.domain.interfaces.similarity_cache import ISimilarityCache


class PickleSimilarityCache(ISimilarityCache):
    def __init__(self, path: Path):
        self.path = path

    async def load(self):
        if not self.path.exists():
            return None

        print("Загружаем данные из кэша")
        with open(self.path, "rb") as f:
            return pickle.load(f)

    async def save(self, matrix):
        self.path.touch()

        with open(self.path, "wb") as f:
            pickle.dump(matrix, f)

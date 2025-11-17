from typing import Protocol


class ISimilarityCache(Protocol):
    async def load(self) -> dict[int, dict[int, float]] | None: ...

    async def save(self, matrix: dict[int, dict[int, float]]) -> None: ...

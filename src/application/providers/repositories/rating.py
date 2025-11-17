from typing import Type, TypeVar

from src.domain.repositories.base import RepositoryInterface
from src.infrastructure.db.uow import UnitOfWork

TRepo = TypeVar("TRepo", bound=RepositoryInterface)


def get_repository(repo_class: Type[TRepo], uow: UnitOfWork) -> TRepo:
    """
    Абстрактная фабрика для создания репозиториев.

    Args:
        repo_class: Класс репозитория, который нужно создать.
        uow: UnitOfWork, к которому будет привязан репозиторий.

    Returns:
        Экземпляр репозитория.
    """
    return repo_class(uow)

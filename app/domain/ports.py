from abc import ABC, abstractmethod
from sqlmodel import SQLModel
from typing import Optional, Union

from .models import MeasurementModel, UserModel


class BaseRepositoryInterface(ABC):
    """
    Базовый класс интерфейса CRUD для репозиториев.
    """

    @abstractmethod
    async def create(
        self, data_list: Union[SQLModel, list[SQLModel]]
    ) -> list[SQLModel]:
        pass

    @abstractmethod
    async def read(self, ids: list[int]) -> Union[SQLModel, None]:
        pass

    @abstractmethod
    async def update(self, id: int, data: dict) -> bool:
        """
        Записывает в поля записи, содержащиеся в ключах словаря data
        значения этих ключей. Если ключа в полях записи нет, это значение
        игнорируется.
        :data: {"имя_поля": значение, ...}
        :return: успех - True, провал - False.
        """
        pass

    @abstractmethod
    async def delete(self, rec_id: int) -> bool:
        """
        :return: успех - True, провал - False.
        """
        pass


class UserRepositoryInterface(BaseRepositoryInterface):
    """
    Расширяет интерфейс CRUD для юзеров специфическими методами.
    """

    @abstractmethod
    async def get_by_login(self, login: str) -> Union[UserModel, None]:
        pass


class MeasurementRepositoryInterface(BaseRepositoryInterface):
    """
    Расширяет интерфейс CRUD для измерений специфическими методами.
    """

    @abstractmethod
    async def get_by_month(self, year: int, month: int) -> list[MeasurementModel]:
        pass

    @abstractmethod
    async def get_distinct_monthes(self) -> list[Optional[tuple]]:
        pass

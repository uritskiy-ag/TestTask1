from domain.ports import UserRepositoryInterface
from domain.models import UserModel, UserModelBase
from sqlalchemy import select
from typing import Optional, Union


class UserDBRepository(UserRepositoryInterface):
    def __init__(self, db_session) -> None:
        self._session = db_session

    async def create(self, data: UserModelBase) -> list[Optional[UserModel]]:
        try:
            user = UserModel(
                name=data.name,
                login=data.login,
                pass_hash=data.pass_hash,
                active=True,
            )
            self._session.add(user)
            await self._session.commit()
            return user
        except Exception as e:
            await self._session.rollback()
            raise e

    async def read(self, ids: Union[int, list[int]]) -> list[Optional[UserModel]]:
        if not isinstance(ids, list):
            ids = [ids]
        statement = select(UserModel).where(UserModel.id in ids)
        result = await self._session.execute(statement)
        db_rec = result.scalars().all()
        return db_rec

    async def update(self, id: int, data: dict) -> bool:
        """
        Записывает в поля записи, содержащиеся в ключах словаря data
        значения этих ключей. Если ключа в полях записи нет, это значение
        игнорируется.
        :data: {"имя_поля": значение, ...}
        :return: успех - True, провал - False.
        """
        raise NotImplementedError

    async def delete(self, rec_id) -> bool:
        """
        :return: успех - True, провал - False.
        """
        raise NotImplementedError

    async def get_by_login(self, login: str) -> list[Optional[UserModel]]:
        statement = select(UserModel).where(UserModel.login == login)
        result = await self._session.execute(statement)
        db_rec = result.scalars().all()
        return db_rec

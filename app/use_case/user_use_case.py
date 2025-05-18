from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
import os
from passlib.context import CryptContext
from typing import Optional, Union

from domain.models import UserModelBase, UserModel
from domain.ports import UserRepositoryInterface


class UserService:
    """
    Основной класс приложения, содержащий логику пользователей.
    """

    def __init__(self, repo: UserRepositoryInterface) -> None:
        self._repo = repo
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    ########## Read ##########

    async def get_by_login(self, login: str) -> UserModel:
        user_rec = await self._repo.get_by_login(login)
        return user_rec

    async def get_by_id(self, id: int) -> UserModel:
        user_rec = await self._repo.read(id)
        return user_rec

    ######### Autentication ##########

    async def register_user(self, form_data: UserModelBase) -> Union[UserModel, None]:
        if self._check_register_data(form_data):
            pass_hash = self._pwd_context.hash(form_data.password)
            user_data = UserModelBase(
                login=form_data.login,
                name=form_data.name,
                pass_hash=pass_hash,
            )
            user = await self._repo.create(user_data)
            return user
        else:
            return None

    async def autenticate_user(
        self,
        form_data: OAuth2PasswordRequestForm,
    ) -> Union[UserModel, None]:
        user = await self._repo.get_by_login(form_data.username)
        if (
            not user
            or len(user) > 1
            or not self._verify_password(form_data.password, user[0].pass_hash)
        ):
            return None
        return user[0]

    @staticmethod
    def create_access_token(
        data: dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        data={"sub": login]}
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            os.environ.get("SECRET_KEY"),
            algorithm=os.environ.get("ALGORITHM"),
        )
        return encoded_jwt

    def _verify_password(self, password: str, pass_hash: str) -> bool:
        return self._pwd_context.verify(password, pass_hash)

    @staticmethod
    def _check_register_data(data: UserModelBase) -> bool:
        return data.login and data.name and data.password

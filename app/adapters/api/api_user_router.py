from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from domain.models import UserModelBase
from use_case.user_use_case import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="autenticate")


def get_user_router(service_factory):
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    router = APIRouter()

    @router.get("/")
    async def root(service: UserService = Depends(service_factory)):
        """
        Публичный. Данные для главной страницы приложения. Для теста заглушка.
        """
        return FileResponse("public/index.html")

    @router.post("/register")
    async def register(
        service: UserService = Depends(service_factory),
        form_data: UserModelBase = Depends(),
    ):
        """
        Публичный. Создание нового юзера.
        В случае успеха возвращает токен доступа.
        :return: dict{"access_token": token: str, "token_type": "bearer"}.
        """
        user = await service.register_user(form_data)
        if not user:
            credentials_exception = HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Некорректные данные для регистрации.",
                headers={"WWW-Authenticate": "Bearer"},
            )
            return credentials_exception
        token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = service.create_access_token(
            {"sub": user.login, "id": user.id}, token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    @router.post("/autenticate")
    async def autenticate(
        service: UserService = Depends(service_factory),
        form_data: OAuth2PasswordRequestForm = Depends(),
    ):
        """
        Публичный, принимает реквизиты для аутентификации.
        В случае успеха возвращает токен доступа.
        :return: dict{"access_token": token: str, "token_type": "bearer"}.
        """
        user = await service.autenticate_user(form_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Некорректный логин или пароль.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = service.create_access_token(
            data={"sub": user.login, "id": user.id}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    return router

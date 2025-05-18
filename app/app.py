from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
import os

from adapters.api.api_user_router import get_user_router
from adapters.api.api_measurement_router import get_measurement_router
from adapters.db.session import db
from adapters.db.measuremeny_db_repo import MeasurementDBRepository
from adapters.db.user_db_repo import UserDBRepository
from use_case.measurement_use_case import MeasurementService
from use_case.user_use_case import UserService


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="autenticate")


def get_user_service(service_type: str):
    REPO_SELECTOR = {
        "db": UserDBRepository,
        # "another_repo_type": UserAnotherRepository,
    }

    async def _get_user_service():
        async with db.get_session() as session:
            repo = REPO_SELECTOR[service_type](session)
            return UserService(repo)

    return _get_user_service


def get_measurement_service(service_type: str):
    REPO_SELECTOR = {
        "db": MeasurementDBRepository,
        # "another_repo_type": MeasurementAnotherRepository,
    }

    async def _get_measurement_service():
        async with db.get_session() as session:
            repo = REPO_SELECTOR[service_type](session)
            return MeasurementService(repo)

    return _get_measurement_service


def get_user_data_from_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token,
            os.environ.get("SECRET_KEY"),
            algorithms=os.environ.get("ALGORITHM"),
        )
        user_data = {"id": payload.get("id"), "login": payload.get("sub")}
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_data
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


app = FastAPI()


user_router = get_user_router(get_user_service(service_type="db"))
measurement_router = get_measurement_router(
    get_measurement_service(service_type="db"),
    get_user_data_from_token,
)
app.include_router(user_router)
app.include_router(measurement_router)

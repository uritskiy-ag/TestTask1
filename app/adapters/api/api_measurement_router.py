from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional

from domain.models import MeasurementModelBase
from use_case.measurement_use_case import MeasurementService


def get_measurement_router(service_factory, get_user_data_from_token):
    router = APIRouter()

    @router.post("/newmeasure")
    async def new_measure(
        measurement_data: MeasurementModelBase,
        service: MeasurementService = Depends(service_factory),
        user_data: dict = Depends(get_user_data_from_token),
    ) -> list[Optional[int]]:
        """
        Приватный. Создает новую запись замера с переданными данными.
        """
        try:
            rec_ids = await service.create_rec(measurement_data, user_data["id"])
        except UserWarning as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=e.args[0],
                headers={"WWW-Authenticate": "Bearer"},
            )
        return rec_ids

    @router.get("/monthlist")
    async def month_list(
        service: MeasurementService = Depends(service_factory),
        user_data: dict = Depends(get_user_data_from_token),
    ) -> list[Optional[tuple]]:
        """
        Приватный. Возвращает список кортежей года и месяца,
        для которых в системе есть замеры.
        """
        month_list = await service.get_month_list()
        return month_list

    @router.get("/monthmeasurements")
    async def get_month_measurements(
        year: int,
        month: int,
        service: MeasurementService = Depends(service_factory),
        user_data: dict = Depends(get_user_data_from_token),
    ):
        """
        Приватный, возвращает список введенных данных об измерениях для
        указанного месяца. Должно выводиться среднее, минимальное и максимальные
        значения по всем концентратам за выбранный месяц.
        """
        records = await service.get_month_measurements(year, month)
        return records

    return router

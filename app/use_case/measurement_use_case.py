from typing import Optional, Union

# from .domain.schema import MeasurementSchema
from domain.models import MeasurementModel, MeasurementModelBase

# from base_use_case import BaseService
from domain.ports import MeasurementRepositoryInterface


class MeasurementService:
    """
    Основной класс приложения, содержащий логику измерений.
    """

    def __init__(self, repo: MeasurementRepositoryInterface):
        self._repo = repo

    ######### Create/Read #########

    async def create_rec(
        self,
        rec_data: Union[
            MeasurementModelBase,
            list[MeasurementModelBase],
        ],
        user_id: int,
    ) -> list[Optional[int]]:
        if not isinstance(rec_data, list):
            rec_data = [rec_data]
        records = await self._repo.create(rec_data, user_id)
        return [rec.id for rec in records]

    async def get_by_id(self, id: int) -> MeasurementModel:
        measurement_rec = await self._repo.read(id)
        return measurement_rec

    ######### Month data ##########

    async def get_month_list(self) -> list[Optional[tuple]]:
        result = await self._repo.get_distinct_monthes()
        return result

    async def get_month_measurements(
        self,
        year: int,
        month: int,
    ) -> dict[list, dict]:
        """
        Возвращает данные измерений и средние, минимальные и максимальные
        значения по всем концентратам за выбранный месяц.
        """
        measurements_data = await self._repo.get_by_month(year, month)
        stat_data = self._compute_stat_data(measurements_data)
        result = {
            "measurements": measurements_data,
            "stat": stat_data,
        }
        return result

    @staticmethod
    def _compute_stat_data(measurements_data: list[Optional[dict]]) -> dict[dict]:
        """
        Вычисляет минимальное и максимальное значения, а так же,
        среднее арифметическое для каждого параметра в списке измерений.
        :return: {"param_a": {"min": min_val, "avg": avg_val, "max": max_val}, ...}
        или пустой словарь, если список замеров пустой.
        """
        if measurements_data:
            grouped_values = {
                key: [rec[key] for rec in measurements_data]
                for key in measurements_data[0].keys()
                if key not in ["raw_material", "measure_date"]
            }
            stat_data = {
                key: {
                    "min": min(grouped_values[key]),
                    "avg": sum(grouped_values[key]) / len(grouped_values[key]),
                    "max": max(grouped_values[key]),
                }
                for key in grouped_values.keys()
            }
        else:
            stat_data = {}
        return stat_data

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from typing import Optional, Union

from domain.ports import MeasurementRepositoryInterface
from domain.models import MeasurementModel, MeasurementModelBase, RawMaterial


class MeasurementDBRepository(MeasurementRepositoryInterface):
    def __init__(self, db_session) -> None:
        self._session = db_session

    async def create(
        self, data_list: MeasurementModelBase, created_by_user: int
    ) -> list[Optional[MeasurementModel]]:
        if not isinstance(data_list, list):
            data_list = [data_list]
        try:
            db_records = []
            for rec in data_list:
                db_records.append(
                    MeasurementModel(
                        raw_material_id=rec.raw_material_id,
                        fe_amount=rec.fe_amount,
                        si_amount=rec.si_amount,
                        al_amount=rec.al_amount,
                        ca_amount=rec.ca_amount,
                        s_amount=rec.s_amount,
                        measure_date=rec.measure_date,
                        create_user=created_by_user,
                        update_user=created_by_user,
                    )
                )
            self._session.add_all(db_records)
            await self._session.commit()
            return db_records
        except IntegrityError as e:
            await self._session.rollback()
            raise UserWarning(
                "Запись с введенными типом сырья и датой замера уже существует."
            )
        except Exception as e:
            await self._session.rollback()
            raise e

    async def read(
        self, ids: Union[int, list[int]]
    ) -> list[Optional[MeasurementModel]]:
        if not isinstance(ids, list):
            ids = [ids]
        statement = select(MeasurementModel).where(MeasurementModel.id in ids)
        result = await self._session.execute(statement)
        db_rec = result.scalars().all()
        return db_rec

    async def update(self, id, data):
        """
        Записывает в поля записи, содержащиеся в ключах словаря data
        значения этих ключей. Если ключа в полях записи нет, это значение
        игнорируется.
        :data: {"имя_поля": значение, ...}
        :return: успех - True, провал - False.
        """
        raise NotImplementedError

    async def delete(self, rec_id):
        """
        :return: успех - True, провал - False.
        """
        raise NotImplementedError

    async def get_by_month(
        self, year: int, month: int
    ) -> list[Optional[MeasurementModel]]:
        statement = (
            select(MeasurementModel, RawMaterial.name)
            .join(RawMaterial, MeasurementModel.raw_material_id == RawMaterial.id)
            .where(MeasurementModel.year == year, MeasurementModel.month == month)
        )
        result = await self._session.execute(statement)
        data = [
            {
                "raw_material": raw_material_name,
                "fe_amount": measurement.fe_amount,
                "si_amount": measurement.si_amount,
                "al_amount": measurement.al_amount,
                "ca_amount": measurement.ca_amount,
                "s_amount": measurement.s_amount,
                "measure_date": measurement.measure_date,
            }
            for measurement, raw_material_name in result
        ]
        return data

    async def get_distinct_monthes(self) -> list[Optional[tuple]]:
        statement = select(MeasurementModel.year, MeasurementModel.month).distinct()
        result = await self._session.execute(statement)
        return [tuple(row) for row in result.all()]

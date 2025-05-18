from datetime import date, datetime
from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint
from sqlalchemy.sql import func, text
from typing import Optional


class CoreFieldsMixin(SQLModel):
    id: int = Field(primary_key=True, sa_column_kwargs={"autoincrement": True})
    create_date: datetime = Field(
        default=func.now(),
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
        },
    )
    create_user: Optional[int] = Field(default=None, foreign_key="users.id")
    update_date: datetime = Field(
        sa_column_kwargs={
            "server_default": text("CURRENT_TIMESTAMP"),
            "onupdate": text("CURRENT_TIMESTAMP"),
        }
    )
    update_user: Optional[int] = Field(default=None, foreign_key="users.id")


class UserModelBase(SQLModel):
    """
    Модель данных юзера без таблицы.
    Часовые пояса и пересчет времени не реализуем.
    """

    login: str
    name: str
    password: Optional[str] = Field(default=None, nullable=True)
    pass_hash: Optional[str] = Field(default=None, nullable=True)


class UserModel(CoreFieldsMixin, UserModelBase, table=True):
    __tablename__ = "users"
    login: str = Field(unique=True, index=True)
    name: str = Field(index=True)
    active: bool = Field(
        default=True,
        sa_column_kwargs={
            "server_default": "True",
        },
    )


class RawMaterial(CoreFieldsMixin, SQLModel, table=True):
    __tablename__ = "raw_material"
    name: str


class MeasurementModelBase(SQLModel):
    """
    Модель данных измерения без таблицы
    """

    raw_material_id: int = Field(foreign_key="raw_material.id")
    fe_amount: float = Field(default=0, ge=0, le=100)
    si_amount: float = Field(default=0, ge=0, le=100)
    al_amount: float = Field(default=0, ge=0, le=100)
    ca_amount: float = Field(default=0, ge=0, le=100)
    s_amount: float = Field(default=0, ge=0, le=100)
    measure_date: date


class MeasurementModel(CoreFieldsMixin, MeasurementModelBase, table=True):
    __tablename__ = "measurements"
    year: Optional[int] = Field(default=None, index=True)
    month: Optional[int] = Field(default=None, index=True)

    def __init__(self, **data):
        super().__init__(**data)
        if self.measure_date:
            self.year = self.measure_date.year
            self.month = self.measure_date.month

    __table_args__ = (
        UniqueConstraint(
            "raw_material_id", "measure_date", name="uix_raw_material_measure_date"
        ),
    )

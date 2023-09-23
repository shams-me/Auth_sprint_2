import typing
from typing import Any, Dict, Generic, Optional, Type, TypeVar, Union
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from models.base import Base
from pydantic import BaseModel
from sqlalchemy import func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).
        **Parameters**
        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model
        self.session = session

    async def get(self, model_id: Any) -> Optional[ModelType]:
        smts = select(self.model).where(self.model.id == model_id).limit(1)
        return await self.session.scalar(smts)

    async def get_multi(self, *, skip: int = 0, limit: int = 100) -> tuple[int, list[ModelType]]:
        smts = select(self.model).offset(skip).limit(limit)
        total = await self.session.scalar(select(func.count("*")))
        return total, (await self.session.scalars(smts)).all()

    async def filter(self, skip: int = 0, limit: int = 100, **kwargs) -> Union[list[ModelType], ModelType, None]:
        smts = select(self.model).filter_by(**kwargs).offset(skip).limit(limit)
        if limit == 1:
            return (await self.session.execute(smts)).scalar_one_or_none()
        else:
            return (await self.session.scalars(smts)).all()

    async def create(self, obj: typing.Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        obj_in_data = jsonable_encoder(obj)
        db_obj = self.model(**obj_in_data)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, *, model_id: int | UUID, data: Union[UpdateSchemaType, Dict[str, Any]]):
        if isinstance(data, dict):
            update_data = data
        else:
            update_data = data.model_dump(exclude_unset=True)

        stmt = update(self.model).where(self.model.id == model_id).values(**update_data)
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete(self, *, model_id: int | UUID) -> Optional[ModelType]:
        obj = await self.get(model_id=model_id)
        if obj:
            await self.session.delete(obj)
            await self.session.commit()
        return

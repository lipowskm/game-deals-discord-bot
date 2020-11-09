from typing import List, Generic, TypeVar, Type
from asyncpg import Record
from database.base import Base
from database.session import database

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        """CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**
        * `model`: A SQLAlchemy model class
        """
        self.model = model

    async def get(self, id: int) -> Record:
        """Return single record from given object ID.

        :param id: Database object id.
        :return: Record object containing data.
        """
        query = self.model.__table__.select().where(id == self.model.id)
        return await database.fetch_one(query=query)

    async def get_by_discord_id(self, discord_id: int) -> Record:
        """Return single record from given object discord ID.

        :param discord_id: Database object discord_id.
        :return: Record object containing data.
        """
        query = self.model.__table__.select().where(discord_id == self.model.discord_id)
        return await database.fetch_one(query=query)

    async def get_by_name(self, name: str) -> Record:
        """Return single record from given object name.

        :param name Database object name.
        :return: Record object containing data.
        """
        query = self.model.__table__.select().where(name == self.model.name)
        return await database.fetch_one(query=query)

    async def get_all(self) -> List[Record]:
        """Return list of all records.

        :return: List of Records objects containing data.
        """
        query = self.model.__table__.select()
        return await database.fetch_all(query=query)

    async def create(self, obj_in: dict) -> int:
        """Create object in database.

        :param obj_in: dict containing required attributes.
        :return: id of created object.
        """
        query = self.model.__table__.insert().values(**obj_in)
        return await database.execute(query=query)

    async def update(self, id: int, obj_in: dict) -> int:
        """Update object with given id.

        :param id: id of updated object in database.
        :param obj_in: dict containing required attributes.
        :return: id of updated object in database.
        """
        db_obj = self.model(**obj_in)
        query = (
            self.model.__table__.update().where(id == self.model.id).values(**db_obj)
        )
        return await database.execute(query=query)

    async def remove(self, id: int) -> int:
        """Remove object with given id.

        :param id: id of object in database.
        :return: id of object in database.
        """
        query = self.model.__table__.delete().where(id == self.model.id)
        return await database.execute(query=query)

    async def remove_all(self) -> int:
        """Remove all rows from table.

        :param id: id of object in database.
        :return: id of object in database.
        """
        query = self.model.__table__.delete()
        return await database.execute(query=query)

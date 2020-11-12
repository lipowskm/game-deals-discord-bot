from typing import List

import discord
from asyncpg import Record

from crud.base import CRUDBase
from database.models import Guild
from database.session import database


class CRUDGuild(CRUDBase[Guild]):
    async def get_all_by_filters(self,
                                 time: int,
                                 auto: bool) -> List[Record]:
        """Return all Guilds which match given filters.

        :param time Hour of the sending deals task execution.
        :param auto If the guild has auto sending enabled.
        :return: List of Record objects containing data.
        """
        query = self.model.__table__.select().where(time == self.model.time and auto == self.model.auto)
        return await database.fetch_all(query=query)

    async def create(self, obj_in: discord.Guild) -> int:
        """Create record in database from discord.Guild class object.

        :param obj_in: discord.Guild object.
        :return: id of created object.
        """
        guild_dict = {
            'discord_id': obj_in.id,
            'name': obj_in.name,
            'auto': True,
            'time': 12
        }
        query = self.model.__table__.insert().values(**guild_dict)
        return await database.execute(query=query)


guild = CRUDGuild(Guild)

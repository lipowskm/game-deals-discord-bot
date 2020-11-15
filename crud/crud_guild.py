from typing import List

import discord
from asyncpg import Record

from crud.base import CRUDBase
from database.models import Guild
from database.session import database


class CRUDGuild(CRUDBase[Guild]):
    async def get_all_by_filters(self, *,
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

    async def update_by_discord_id(self, discord_id: int, obj_in: dict) -> int:
        """Update object with given id.

        :param discord_id: id of updated Guild in discord.
        :param obj_in: dict containing required attributes.
        :return: id of updated object in database.
        """
        query = (
            self.model.__table__.update().where(discord_id == self.model.discord_id).values(**obj_in)
        )
        return await database.execute(query=query)

    async def remove_by_discord_id(self, discord_id: int) -> int:
        """Remove Guild with given discord ID.

        :param discord_id: ID of Guild in Discord.
        :return: id of object in database.
        """
        query = self.model.__table__.delete().where(discord_id == self.model.discord_id)
        return await database.execute(query=query)


guild = CRUDGuild(Guild)

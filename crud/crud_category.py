from typing import Tuple, Union

import discord

import crud
from crud.base import CRUDBase
from database.models import Category
from database.session import database


class CRUDCategory(CRUDBase[Category]):
    async def get_by_guild_id(self, guild_id: int) -> int:
        """Get category by id of the Guild in database.

        :param guild_id: id of Guild in database.
        :return: Record object containing data.
        """
        query = self.model.__table__.select().where(self.model.guild_id == guild_id)
        return await database.fetch_one(query=query)

    async def create_with_relationship(self,
                                       category_in: discord.CategoryChannel,
                                       guild_in: Union[discord.Guild, int]) -> Tuple[int, int]:
        """Create record in database from discord.CategoryChannel class object with relationship to provided guild.
        If the guild is not in database, it is created first.

        :param category_in: discord.CategoryChannel object.
        :param guild_in: discord.Guild object or ID of the guild in the database.
        :return: id of created Guild and id of created Category
        """
        if type(guild_in) == discord.Guild:
            guild = await crud.guild.get_by_name(guild_in.name)
        else:
            guild = await crud.guild.get(guild_in)
        if not guild:
            db_guild_id = await crud.guild.create(guild_in)
        else:
            db_guild_id = dict(guild)['id']
        category_dict = {
            'discord_id': category_in.id,
            'name': category_in.name,
            'guild_id': db_guild_id
        }
        query = self.model.__table__.insert().values(**category_dict)
        return db_guild_id, await database.execute(query=query)


category = CRUDCategory(Category)

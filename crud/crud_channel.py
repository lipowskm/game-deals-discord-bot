from typing import List

import discord
from asyncpg import Record

import crud
from crud.base import CRUDBase
from database.models import Channel, Category
from database.session import database


class CRUDChannel(CRUDBase[Channel]):
    async def get_by_name(self, name: str) -> Record:
        query = self.model.__table__.select().where(name == self.model.name)
        return await database.fetch_one(query=query)

    async def create(self, obj_in: discord.TextChannel) -> int:
        """Create record in database from discord.TextChannel class object.

        :param obj_in: discord.TextChannel object.
        :return: id of created object.
        """
        guild_dict = {
            'discord_id': obj_in.id,
            'name': obj_in.name
        }
        query = self.model.__table__.insert().values(**guild_dict)
        return await database.execute(query=query)

    async def bulk_create(self,
                          channels_in: List[discord.TextChannel],
                          category_in: discord.CategoryChannel,
                          guild_in: discord.Guild) -> None:
        """Create multiple records in database from discord.TextChannel class objects.
        It requires proving a category and guild to create relationships.

        :param channels_in: List of discord.TextChannel object.
        :param category_in: discord.CategoryChannel object.
        :param guild_in: discord.CategoryChannel object.
        :return: None.
        """
        category = await crud.category.get_by_name(category_in.name)
        if not category:
            db_category_id = await crud.category.create_with_relationship(category_in, guild_in)
        else:
            db_category_id = dict(category)['id']
        channels_list = []
        for channel_in in channels_in:
            channel_dict = {
                'discord_id': channel_in.id,
                'name': channel_in.name,
                'category_id': db_category_id
            }
            channels_list.append(channel_dict)
        query = self.model.__table__.insert().values(channels_list)
        await database.execute(query=query)


channel = CRUDChannel(Channel)

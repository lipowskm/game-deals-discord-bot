from typing import List

import discord
from typing import Union

import crud
from crud.base import CRUDBase
from database.models import Channel
from database.session import database


class CRUDChannel(CRUDBase[Channel]):
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
                          category_in: Union[discord.CategoryChannel, int],
                          guild_in: Union[discord.Guild, int]) -> None:
        """Create multiple records in database from discord.TextChannel class objects.
        It requires proving a category and guild to create relationships.

        :param channels_in: List of discord.TextChannel object.
        :param category_in: discord.CategoryChannel object or ID of category in database.
        :param guild_in: discord.Guild object or ID of guild in database.
        :return: None.
        """
        if type(category_in) == discord.CategoryChannel:
            category = await crud.category.get_by_name(category_in.name)
        else:
            category = await crud.category.get(category_in)
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

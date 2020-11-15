from typing import List

import discord
from typing import Union

import crud
import settings
from crud.base import CRUDBase
from database.models import Channel
from database.session import database


class CRUDChannel(CRUDBase[Channel]):
    async def get_all_by_guild_id(self, guild_id: int) -> int:
        """Get all channels by id of the Guild in database.

        :param guild_id: id of Guild in database.
        :return: List of Records objects containing data.
        """
        query = self.model.__table__.select().where(self.model.guild_id == guild_id)
        return await database.fetch_all(query=query)

    async def get_all_by_guild_discord_id(self, guild_discord_id: int) -> int:
        """Get all channels by id of the Guild in Discord.

        :param guild_discord_id: id of Guild in Discord.
        :return: List of Records objects containing data.
        """
        query = self.model.__table__.select().where(self.model.guild_discord_id == guild_discord_id)
        return await database.fetch_all(query=query)

    async def get_all_by_category_id(self, category_id: int) -> int:
        """Get all channels by id of the Category in database.

        :param category_id: id of Category in database.
        :return: List of Records objects containing data.
        """
        query = self.model.__table__.select().where(self.model.category_id == category_id)
        return await database.fetch_all(query=query)

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
            db_category = await crud.category.get_by_discord_id(category_in.id)
        else:
            db_category = await crud.category.get(category_in)
        if not db_category:
            db_guild_id, db_category_id = await crud.category.create_with_relationship(category_in, guild_in)
            db_category = await crud.category.get(db_category_id)
        else:
            db_guild_id = db_category['guild_id']
            db_category_id = db_category['id']
        db_guild = await crud.guild.get(db_guild_id)
        channels_list = []
        for channel_in in channels_in:
            channel_dict = {
                'discord_id': channel_in.id,
                'name': channel_in.name,
                'category_id': db_category_id,
                'guild_id': db_guild_id,
                'category_discord_id': db_category['discord_id'],
                'guild_discord_id': db_guild['discord_id'],
                'min_retail_price': settings.CHANNELS_SETTINGS[channel_in.name]['min_retail_price'],
                'max_retail_price': settings.CHANNELS_SETTINGS[channel_in.name]['max_retail_price'],
                'store': settings.CHANNELS_SETTINGS[channel_in.name]['store'],
            }
            channels_list.append(channel_dict)
        query = self.model.__table__.insert().values(channels_list)
        await database.execute(query=query)

    async def update_by_name(self, name: str, obj_in: dict) -> int:
        """Update object with given name.

        :param name: name of updated Channel in database.
        :param obj_in: dict containing required attributes.
        :return: id of updated object in database.
        """
        query = (
            self.model.__table__.update().where(name == self.model.name).values(**obj_in)
        )
        return await database.execute(query=query)

    async def update_by_discord_id(self, discord_id: int, obj_in: dict) -> int:
        """Update object with given id.

        :param discord_id: ID of updated Channel in Discord.
        :param obj_in: dict containing required attributes.
        :return: id of updated object in database.
        """
        query = (
            self.model.__table__.update().where(discord_id == self.model.discord_id).values(**obj_in)
        )
        return await database.execute(query=query)


channel = CRUDChannel(Channel)

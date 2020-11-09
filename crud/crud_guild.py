import discord

from crud.base import CRUDBase
from database.models import Guild
from database.session import database


class CRUDGuild(CRUDBase[Guild]):
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

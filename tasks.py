import asyncio
import logging
from datetime import datetime
from typing import List

import discord
from asyncpg import Record
from discord.ext import commands, tasks

import crud
import settings
from deal import Deal, get_deals, get_embed_from_deal

guilds__running_tasks: dict = {}


class ScheduledTasks(commands.Cog):
    """Cog designed for tasks that are handled by the bot automatically.
    """
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.deals_schedule.start()

    @tasks.loop(minutes=1)
    async def deals_schedule(self):
        """Every hour sends deals to every guild asynchronously which has this hour set up as a delivery hour.

        :return: None
        """
        if not datetime.now().minute == 0:
            return
        steam_deals_list = await get_deals(amount=settings.STEAM_DEALS_AMOUNT, store='steam')
        gog_deals_list = await get_deals(amount=settings.GOG_DEALS_AMOUNT, store='gog')
        coroutines = []
        db_guilds = await crud.guild.get_all_by_filters(time=datetime.now().hour, auto=True)
        if not db_guilds:
            return
        for db_guild in db_guilds:
            db_guild = dict(db_guild)
            guild = self.bot.get_guild(db_guild['discord_id'])
            coroutines.append(self.deals_task(guild, steam_deals_list + gog_deals_list))
        await asyncio.gather(*coroutines)

    @deals_schedule.before_loop
    async def before_deals_schedule(self):
        await self.bot.wait_until_ready()

    async def deals_task(self,
                         guild: discord.Guild,
                         deals_list: List[Deal]):
        """Creates new task object and tries to send deals to every channel that is assigned to the Guild in database.
        After it's done, removes task object for the Guild.

        :param guild: discord.py Guild class object to send deals to.
        :param deals_list: List of Deal dataclass objects.
        :return: None
        """
        if guild.id in guilds__running_tasks.keys():
            guilds__running_tasks[guild.id].append(self.deals_task.__name__)
        else:
            guilds__running_tasks[guild.id] = [self.deals_task.__name__]

        try:
            db_channels = await crud.channel.get_all_by_guild_discord_id(guild.id)
            await self.send_deals_to_channels(deals_list,
                                              db_channels)

        except discord.errors.Forbidden:
            logging.error(f'Insufficient permissions to send messages or bot has been removed from {guild}')
        guilds__running_tasks[guild.id].remove(self.deals_task.__name__)

    async def send_deals_to_channel(self,
                                    deals_list: List[Deal],
                                    channel: discord.TextChannel):
        """Method that sends deals to the channel specified.

        :param deals_list: List of Deal dataclass objects.
        :param channel: discord.py Channel class object.
        :return: None
        """
        if len(deals_list) == 0:
            return
        try:
            await channel.purge()
            await asyncio.sleep(1)  # This is due to the Discord sometimes not clearing the channel.
            await channel.send(content=f"**Here's a list of {len(deals_list)} new :video_game: deals!**")
            await channel.send(content=f"```Last updated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')} UTC```")
            for deal in deals_list:
                await channel.send(embed=get_embed_from_deal(deal))
            await channel.send(content="```That's it for today :(```")
        except discord.errors.NotFound:
            logging.error(f'Channel {channel.name} has been deleted while the bot was working on {channel.guild}')
            new_channel = await channel.guild.create_text_channel(name=channel.name, category=channel.category)
            await crud.channel.update_by_discord_id(channel.id, {'discord_id': new_channel.id,
                                                                 'name': channel.name})
            await self.send_deals_to_channel(deals_list, new_channel)

    async def send_deals_to_channels(self,
                                     deals_list: List[Deal],
                                     db_channels: List[Record]):
        """Method that takes list of channels from database, filters the deals basing on fields
        (minimum and maximum retail price) in database for each channel, and sends the filtered deals to all channels
        asynchronously.

        :param deals_list: List od Deal dataclass objects.
        :param db_channels: List of channels gathered from database.
        :return: None
        """
        coroutines = []
        for db_channel in db_channels:
            db_channel = dict(db_channel)
            channel = self.bot.get_channel(db_channel['discord_id'])
            filtered_deals = [deal for deal in deals_list
                              if deal.store_id == settings.STORES_MAPPING[db_channel['store']]
                              and db_channel['min_retail_price'] < deal.normal_price <= db_channel['max_retail_price']]
            coroutines.append(self.send_deals_to_channel(filtered_deals, channel))
        await asyncio.gather(*coroutines)

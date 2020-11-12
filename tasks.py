import asyncio
import logging
from asyncpg import Record
from datetime import datetime
from typing import List

import discord
from discord.ext import commands, tasks

import crud
import settings
from deal import get_deals, get_embed_from_deal, Deal

guilds__running_tasks: dict = {}


async def initialize_channels(guild: discord.Guild) -> (discord.CategoryChannel, List[discord.TextChannel]):
    if not discord.utils.find(lambda c: c.name == settings.CATEGORY, guild.categories):
        category = await guild.create_category(name=settings.CATEGORY)
    else:
        category = discord.utils.get(guild.categories, name=settings.CATEGORY)
    for role in guild.roles:
        await category.set_permissions(role, send_messages=False)
    await category.set_permissions(guild.me, send_messages=True)

    channels_list = []

    for channel_name in settings.CHANNELS_SETTINGS.keys():
        channel = discord.utils.find(lambda c: c.name == channel_name
                                     and c.category_id == category.id, guild.channels)
        if not channel:
            channel = await guild.create_text_channel(name=channel_name, category=category)
        channels_list.append(channel)

    return category, channels_list


class ScheduledTasks(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.deals_schedule.start()

    @tasks.loop(minutes=60)
    async def deals_schedule(self):
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
        if len(deals_list) == 0:
            return
        try:
            await channel.purge()
            await asyncio.sleep(1)  # This is due to the Discord sometimes not clearing the channel.
            await channel.send(content=f"```Last updated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}```")
            await channel.send(content=f"```Here's a list of {len(deals_list)} new deals!```")
            for deal in deals_list:
                await channel.send(embed=get_embed_from_deal(deal))
            await channel.send(content=f"```That's it for today :(```")
        except discord.errors.NotFound:
            logging.error(f'Channel {channel.name} has been deleted while the bot was working on {channel.guild}')
            new_channel = await channel.guild.create_text_channel(name=channel.name, category=channel.category)
            await crud.channel.update_by_discord_id(channel.id, {'discord_id': new_channel.id})
            await self.send_deals_to_channel(deals_list, new_channel)

    async def send_deals_to_channels(self,
                                     deals_list: List[Deal],
                                     db_channels: List[Record]):
        coroutines = []
        for db_channel in db_channels:
            db_channel = dict(db_channel)
            channel = self.bot.get_channel(db_channel['discord_id'])
            filtered_deals = [deal for deal in deals_list
                              if deal.store_id == settings.STORES_MAPPING[db_channel['store']]
                              and db_channel['min_retail_price'] < deal.normal_price <= db_channel['max_retail_price']]
            coroutines.append(self.send_deals_to_channel(filtered_deals, channel))
        await asyncio.gather(*coroutines)

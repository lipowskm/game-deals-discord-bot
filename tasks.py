import asyncio
import logging
from datetime import datetime
from typing import List

import discord
from discord.ext import commands, tasks

import settings
from deal import get_deals, get_embed_from_deal, Deal

guilds__running_tasks: dict = {}


async def send_deals_to_channel(deals_list: List[Deal],
                                channel: discord.TextChannel):
    if len(deals_list) == 0:
        return
    await channel.purge()
    await asyncio.sleep(1)  # This is due to the Discord sometimes not clearing the channel.
    await channel.send(content=f"```Last updated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}```")
    await channel.send(content=f"```Here's a list of {len(deals_list)} new deals!```")
    for deal in deals_list:
        await channel.send(embed=get_embed_from_deal(deal))
    await channel.send(content=f"```That's it for today :(```")


async def send_deals_to_channels(deals_list: List[Deal],
                                 steam_channel: discord.TextChannel,
                                 steam_aaa_channel: discord.TextChannel,
                                 gog_channel: discord.TextChannel,
                                 gog_aaa_channel: discord.TextChannel):
    steam_deals = []
    steam_aaa_deals = []
    gog_deals = []
    gog_aaa_deals = []
    for deal in deals_list:
        if deal.store_id == '1' and deal.normal_price <= 29:
            steam_deals.append(deal)
        if deal.store_id == '1' and deal.normal_price > 29:
            steam_aaa_deals.append(deal)
        if deal.store_id == '7' and deal.normal_price <= 29:
            gog_deals.append(deal)
        if deal.store_id == '7' and deal.normal_price > 29:
            gog_aaa_deals.append(deal)

    coroutines = [send_deals_to_channel(steam_deals, steam_channel),
                  send_deals_to_channel(steam_aaa_deals, steam_aaa_channel),
                  send_deals_to_channel(gog_deals, gog_channel),
                  send_deals_to_channel(gog_aaa_deals, gog_aaa_channel)]
    await asyncio.gather(*coroutines)


async def create_missing_channels(guild: discord.Guild):
    if not discord.utils.find(lambda c: c.name == settings.CATEGORY, guild.categories):
        category = await guild.create_category(name=settings.CATEGORY)
    else:
        category = discord.utils.get(guild.categories, name=settings.CATEGORY)
    for role in guild.roles:
        await category.set_permissions(role, send_messages=False)
    await category.set_permissions(guild.me, send_messages=True)

    for channel in settings.CHANNELS:
        if not discord.utils.find(lambda c: c.name == channel and c.category_id == category.id, guild.channels):
            channel = await guild.create_text_channel(name=channel, category=category)


async def deals_task(guild: discord.Guild,
                     deals_list: List[Deal]):
    if guild.id in guilds__running_tasks.keys():
        guilds__running_tasks[guild.id].append(deals_task.__name__)
    else:
        guilds__running_tasks[guild.id] = [deals_task.__name__]

    try:
        category = discord.utils.get(guild.categories, name=settings.CATEGORY)
        steam_channel = discord.utils.get(guild.channels, name=settings.STEAM_CHANNEL, category=category)
        steam_aaa_channel = discord.utils.get(guild.channels, name=settings.STEAM_AAA_CHANNEL, category=category)
        gog_channel = discord.utils.get(guild.channels, name=settings.GOG_CHANNEL, category=category)
        gog_aaa_channel = discord.utils.get(guild.channels, name=settings.GOG_AAA_CHANNEL, category=category)

        await send_deals_to_channels(deals_list,
                                     steam_channel,
                                     steam_aaa_channel,
                                     gog_channel,
                                     gog_aaa_channel)

    except discord.errors.Forbidden:
        logging.error(f'Insufficient permissions to send messages or bot has been removed from {guild}')
    except discord.errors.NotFound:
        logging.error(f'Channel has been deleted while the bot was working on {guild}')
        await create_missing_channels(guild)
    guilds__running_tasks[guild.id].remove(deals_task.__name__)


class ScheduledTasks(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.deals_schedule.start()

    @tasks.loop(minutes=60)
    async def deals_schedule(self):
        if datetime.now().hour == 12:
            steam_deals_list = await get_deals(amount=settings.STEAM_DEALS_AMOUNT, store='steam')
            gog_deals_list = await get_deals(amount=settings.GOG_DEALS_AMOUNT, store='gog')
            coroutines = [deals_task(guild,
                                     steam_deals_list +
                                     gog_deals_list) for guild in self.bot.guilds]
            await asyncio.gather(*coroutines)

    @deals_schedule.before_loop
    async def before_deals_schedule(self):
        await self.bot.wait_until_ready()
        coroutines = [create_missing_channels(guild) for guild in self.bot.guilds]
        await asyncio.gather(*coroutines)

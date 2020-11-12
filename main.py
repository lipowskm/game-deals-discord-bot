import asyncio

import crud
from commands import Commands
import settings
import database.base
from database.base import Base
from database.session import database, engine
from deal import get_deals
from tasks import initialize_channels, ScheduledTasks
import logging

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix=settings.PREFIX + ' ')


@bot.event
async def on_guild_join(guild: discord.Guild):
    logging.info(f'Joined guild {guild.name}')
    category, channels = await initialize_channels(guild)
    db_guild = await crud.guild.get_by_discord_id(guild.id)
    if not db_guild:
        await crud.channel.bulk_create(channels, category, guild)
    else:
        db_category = dict(await crud.category.get_by_guild_id(dict(db_guild)['id']))
        if db_category['discord_id'] != category.id:
            await crud.category.update(db_category['id'], {'discord_id': category.id})
        for channel in channels:
            await crud.channel.update_by_name(channel.name, {'discord_id': channel.id})

    steam_deals_list = await get_deals(amount=settings.STEAM_DEALS_AMOUNT, store='steam')
    gog_deals_list = await get_deals(amount=settings.GOG_DEALS_AMOUNT, store='gog')
    scheduled_tasks_cog: ScheduledTasks = bot.get_cog("ScheduledTasks")
    await scheduled_tasks_cog.deals_task(guild, steam_deals_list + gog_deals_list)


@bot.event
async def on_command_error(ctx: commands.Context, error):
    if hasattr(ctx.command, 'on_error'):
        return

    if isinstance(error, discord.ext.commands.CommandNotFound):
        await ctx.channel.send('```fix\n'
                               'Unknown command\n'
                               f'Type  {settings.PREFIX} help  for possible commands```')


@bot.event
async def on_ready():
    Base.metadata.create_all(engine)

    await bot.change_presence(status=discord.Status.online, activity=discord.Game(f"Listening on {settings.PREFIX}"))
    logging.info('Bot started')
    try:
        open('config.yaml', 'x')
        logging.info('Created new config file')
    except FileExistsError:
        pass


@bot.event
async def on_connect():
    await database.connect()


@bot.event
async def on_disconnect():
    await bot.change_presence(status=discord.Status.idle, activity=discord.Game(f"Disconnected"))
    logging.info('Bot disconnected')


@bot.event
async def on_resumed():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(f"Listening on {settings.PREFIX}"))
    logging.info('Bot restarted')


logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=logging.INFO)
bot.add_cog(ScheduledTasks(bot))
bot.add_cog(Commands(bot))

bot.run(settings.BOT_TOKEN)

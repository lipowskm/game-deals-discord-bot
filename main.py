import logging

import discord
from discord.ext import commands

import crud
import database.base
import settings
from commands import Commands
from database.base import Base
from database.session import database, engine
from deal import get_deals
from tasks import ScheduledTasks
from utils import initialize_channels

bot = commands.Bot(command_prefix=settings.PREFIX + ' ')


@bot.event
async def on_guild_join(guild: discord.Guild):
    logging.info(f'Joined guild {guild.name}')
    try:
        category, channels = await initialize_channels(guild)
        if not await crud.guild.get_by_discord_id(guild.id):
            await crud.channel.bulk_create(channels, category, guild)

        steam_deals_list = await get_deals(amount=settings.STEAM_DEALS_AMOUNT, store='steam')
        gog_deals_list = await get_deals(amount=settings.GOG_DEALS_AMOUNT, store='gog')
        scheduled_tasks_cog: ScheduledTasks = bot.get_cog("ScheduledTasks")
        await scheduled_tasks_cog.deals_task(guild, steam_deals_list + gog_deals_list)
    except discord.errors.Forbidden:
        logging.info(f'Leaving guild {guild.name} because of insufficient permissions')
        await guild.leave()
        return


@bot.event
async def on_guild_remove(guild: discord.Guild):
    logging.info(f'Bot has been removed from {guild.name}')
    await crud.guild.remove_by_discord_id(guild.id)


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


@bot.event
async def on_connect():
    await database.connect()


@bot.event
async def on_disconnect():
    logging.info('Bot disconnected')


@bot.event
async def on_resumed():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(f"Listening on {settings.PREFIX}"))
    logging.info('Bot restarted')


@bot.event
async def on_guild_channel_update(before: discord.TextChannel, after: discord.TextChannel):
    if not isinstance(before, discord.TextChannel):
        return
    db_channels = await crud.channel.get_all_by_guild_discord_id(before.guild.id)
    for db_channel in db_channels:
        if before.id == db_channel['discord_id'] and after.name != db_channel['name']:
            await crud.channel.update(db_channel['id'], {'name': after.name})
            break


logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=logging.INFO)
bot.add_cog(ScheduledTasks(bot))
bot.add_cog(Commands(bot))

bot.run(settings.BOT_TOKEN)

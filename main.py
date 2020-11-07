from commands import Commands
import settings
from deal import get_deals
from tasks import deals_task, create_missing_channels, ScheduledTasks
import logging

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix=settings.PREFIX + ' ')


@bot.event
async def on_guild_join(guild: discord.Guild):
    logging.info(f'Joined guild {guild.name}')
    await create_missing_channels(guild)
    deals_list = await get_deals()
    await deals_task(guild, deals_list)


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
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(f"Listening on {settings.PREFIX}"))
    logging.info('Bot started')


logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=logging.INFO)
bot.add_cog(ScheduledTasks(bot))
bot.add_cog(Commands(bot))
if settings.PRODUCTION:
    bot.run(settings.BOT_TOKEN)
else:
    bot.run(settings.BOT_TOKEN_DEV)

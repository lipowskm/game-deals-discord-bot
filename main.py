from commands import Commands
import settings
from deal import get_deals
from tasks import create_missing_channels, ScheduledTasks
import logging
import yaml

import discord
from discord.ext import commands

bot = commands.Bot(command_prefix=settings.PREFIX + ' ')


@bot.event
async def on_guild_join(guild: discord.Guild):
    logging.info(f'Joined guild {guild.name}')
    category, channels = await create_missing_channels(guild)
    with open('config.yaml', 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        guild_config = {
            guild.id: {
                'category': category.id,
                'channels': {channel.name: channel.id for channel in channels},
                'auto': True,
                'time': 12
            }
        }
        if config:
            config.update(guild_config)
        else:
            config = guild_config
    with open('config.yaml', 'w') as f:
        yaml.safe_dump(config, stream=f)
        logging.info(f'Updated config.yaml for guild {guild.name}')
    deals_list = await get_deals()
    scheduled_tasks_cog: ScheduledTasks = await bot.get_cog("ScheduledTasks")
    await scheduled_tasks_cog.deals_task(guild, deals_list)


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
    try:
        open('config.yaml', 'x')
        logging.info('Created new config file')
    except FileExistsError:
        pass


logging.basicConfig(format="%(asctime)s %(levelname)s: %(message)s", level=logging.INFO)
bot.add_cog(ScheduledTasks(bot))
bot.add_cog(Commands(bot))

bot.run(settings.BOT_TOKEN)

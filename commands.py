import asyncio

import discord

import crud
import settings
from discord.ext import commands

import strings
from deal import get_embed_from_deal, NoDealsFound, get_random_deal, get_deals
from tasks import guilds__running_tasks, ScheduledTasks


class Commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot
        self.scheduled_tasks_cog: ScheduledTasks = self.bot.get_cog('ScheduledTasks')

    @commands.command(name='update',
                      brief=strings.COMMAND_UPDATE_BRIEF,
                      description=strings.COMMAND_UPDATE_DESC)
    @commands.has_permissions(administrator=True)
    async def update(self, ctx: commands.Context, store: str = 'all', deals_amount: int = 60):
        try:
            deals_amount = int(store)
            store = 'all'
        except ValueError:
            pass
        if ctx.guild.id in guilds__running_tasks.keys() and \
                self.scheduled_tasks_cog.deals_task.__name__ in guilds__running_tasks[ctx.guild.id]:
            await ctx.send('```fix\nBot is already updating, please wait...```')
            return
        if deals_amount > 200:
            await ctx.send('```fix\nMaximum amount of deals is 200\nPlease provide another amount```')
            return
        try:
            if store in ['steam', 'gog', 'all']:
                await ctx.send(f'```Started updating daily deals for {store.capitalize()}```')
                deals_list = await get_deals(amount=deals_amount, store=store)
                await self.scheduled_tasks_cog.deals_task(ctx.guild, deals_list)
                await ctx.send(f'```{store.capitalize()} deals have been updated with {len(deals_list)} positions```')
            else:
                raise discord.ext.commands.BadArgument
        except NoDealsFound:
            await ctx.send(f'```Could not find any deals to show```')

    @update.error
    async def update_handler(self, ctx: commands.Context, error):
        """A local Error Handler for update command.
        """

        if isinstance(error, discord.ext.commands.BadArgument):
            await ctx.channel.send('```fix\n'
                                   'Invalid option\n\n'
                                   'Possible options:\n'
                                   f'{settings.PREFIX} update <steam, gog> [deals_amount]\n\n'
                                   'Example:\n'
                                   f'{settings.PREFIX} update steam 10```')
        if isinstance(error, discord.ext.commands.MissingPermissions):
            await ctx.channel.send('```fix\n'
                                   'Only administrators are allowed to use this command```')

    @commands.command(name='random',
                      brief=strings.COMMAND_RANDOM_BRIEF,
                      description=strings.COMMAND_RANDOM_DESC)
    async def random(self, ctx: commands.Context, min_price: int = 0):
        try:
            deal = await get_random_deal(min_price)
        except NoDealsFound:
            await ctx.send(content='```Unable to find random deal with provided minimum discount price```')
            return
        await ctx.send(content=f"Here's a random deal for you, **{ctx.author.name}**!",
                       embed=get_embed_from_deal(deal))

    @random.error
    async def random_handler(self, ctx: commands.Context, error):
        """A local Error Handler for random command.
        """

        if isinstance(error, discord.ext.commands.BadArgument):
            await ctx.channel.send('```fix\n'
                                   'Invalid option\n'
                                   'Option must be an integer\n\n'
                                   'Possible options:\n'
                                   f'{settings.PREFIX} random [min_price]\n\n'
                                   'Example:\n'
                                   f'{settings.PREFIX} random 5```')

    @commands.command(name='flip',
                      brief=strings.COMMAND_FLIP_BRIEF,
                      description=strings.COMMAND_FLIP_DESC)
    async def flip(self, ctx: commands.Context, min_price: int = 0, max_price: int = 60):
        try:
            deals_list = await get_deals(min_price=min_price, max_price=max_price, amount=60)
        except NoDealsFound:
            await ctx.send(content=f'```No deals found within specified price range```')
            return
        start_message = await ctx.send(content=f"```Here's a flipbook of deals for you, {ctx.author.name}!```")
        pages = len(deals_list)
        current_page = 1
        deal = deals_list[0]
        message = await ctx.send(content=f'**Page {current_page}/{pages}**',
                                 embed=get_embed_from_deal(deal))
        await message.add_reaction('◀️')
        await message.add_reaction('▶️')
        active = True

        def check(_reaction, _user):
            return (_user != self.bot.user
                    and str(_reaction.emoji) in ['◀️', '▶️']
                    and _reaction.message == message)

        while active:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=120, check=check)

                if user != ctx.author:
                    await message.remove_reaction(reaction, user)
                    continue

                if str(reaction.emoji) == '▶️':
                    if current_page == pages:
                        current_page = 1
                    else:
                        current_page += 1
                    deal = deals_list[current_page - 1]
                    await message.edit(content=f'**Page {current_page}/{pages}**',
                                       embed=get_embed_from_deal(deal))
                    await message.remove_reaction(reaction, user)

                if str(reaction.emoji) == '◀️':
                    if current_page == 1:
                        current_page = pages
                    else:
                        current_page -= 1
                    deal = deals_list[current_page - 1]
                    await message.edit(content=f'**Page {current_page}/{pages}**',
                                       embed=get_embed_from_deal(deal))
                    await message.remove_reaction(reaction, user)
            except asyncio.TimeoutError:
                await start_message.delete()
                await message.delete()
                active = False

    @flip.error
    async def flip_handler(self, ctx: commands.Context, error):
        """A local Error Handler for flip command.
        """

        if isinstance(error, discord.ext.commands.BadArgument):
            await ctx.channel.send('```fix\n'
                                   'Invalid option\n'
                                   'Options must be an integers\n\n'
                                   'Possible options:\n'
                                   f'{settings.PREFIX} flip [min_price] [max_price]\n\n'
                                   'Example:\n'
                                   f'{settings.PREFIX} flip 15\n'
                                   f'{settings.PREFIX} flip 5 10```')

    @commands.group()
    @commands.has_permissions(administrator=True)
    async def auto(self, ctx: commands.Context):
        if not ctx.invoked_subcommand:
            await ctx.channel.send('```fix\n'
                                   'Invalid subcommand\n'
                                   'Possible subommands:\n\n'
                                   f'{settings.PREFIX} auto enable\n'
                                   f'{settings.PREFIX} auto disable\n'
                                   f'{settings.PREFIX} auto time [hour]```')

    @auto.command()
    async def enable(self, ctx: commands.Context):
        db_guild = await crud.guild.get_by_discord_id(ctx.guild.id)
        if db_guild['auto']:
            await ctx.send(content=f'```fix\nAutomatic updates are already enabled```')
            return
        await crud.guild.update(db_guild['id'], {'auto': True})
        await ctx.send(content=f'```Automatic updates have been enabled```')

    @auto.command()
    async def disable(self, ctx: commands.Context):
        db_guild = await crud.guild.get_by_discord_id(ctx.guild.id)
        if not db_guild['auto']:
            await ctx.send(content=f'```fix\nAutomatic updates are already disabled```')
            return
        await crud.guild.update(db_guild['id'], {'auto': False})
        await ctx.send(content=f'```Automatic updates have been disabled```')

    @auto.command()
    async def time(self, ctx: commands.Context, hour: int = None):
        if not hour:
            db_guild = await crud.guild.get_by_discord_id(ctx.guild.id)
            await ctx.send(content=f"```Automatic updates are scheduled for {db_guild['time']}:00 UTC```")
            return
        if not 0 <= hour < 24:
            await ctx.send(content=f'```fix\nTime of auto update has to be a number between 0 and 23```')
            return
        db_guild = await crud.guild.get_by_discord_id(ctx.guild.id)
        await crud.guild.update(db_guild['id'], {'time': hour})
        await ctx.send(content=f'```Update time has been set to {hour}:00 UTC```')

    @time.error
    async def time_handler(self, ctx: commands.Context, error):
        """A local Error Handler for time command.
        """

        if isinstance(error, discord.ext.commands.BadArgument):
            await ctx.channel.send('```fix\n'
                                   'Invalid argument\n'
                                   'Argument must be an integer between 0 and 23\n\n'
                                   'Example:\n'
                                   f'{settings.PREFIX} auto time 12```')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.content == settings.PREFIX:
            await message.channel.send('```fix\n'
                                       'Options required\n'
                                       f'Type  {settings.PREFIX} help  for possible options```')

from typing import List

import discord

import settings


async def initialize_channels(guild: discord.Guild) -> (discord.CategoryChannel, List[discord.TextChannel]):
    """Function that checks whether all channels and category required by the bot are present in the Guild,
    and if not, creates them.

    :param guild: discord.py Guild class object.
    :return: tuple of discord.py Category class object and list of Channel class objects.
    """
    if not discord.utils.find(lambda c: c.name == settings.CATEGORY, guild.categories):
        category = await guild.create_category(name=settings.CATEGORY)
    else:
        category = discord.utils.get(guild.categories, name=settings.CATEGORY)
#     for role in guild.roles:
#         await category.set_permissions(role, send_messages=False)
    await category.set_permissions(guild.me, send_messages=True)

    channels_list = []

    for channel_name in settings.CHANNELS_SETTINGS.keys():
        channel = discord.utils.find(lambda c: c.name == channel_name
                                     and c.category_id == category.id, guild.channels)
        if not channel:
            channel = await guild.create_text_channel(name=channel_name, category=category)
        channels_list.append(channel)

    return category, channels_list


def replace_all(text: str, replace_dict: dict) -> str:
    """Helper function to replace multiple characters in a string.

    :param text: String to be formatted.
    :param replace_dict: Dictionary containing characters to replace. Keys are characters to be replaced,
        values are characters to be inserted instead.
    :return: Formatted string.
    """
    for i, j in replace_dict.items():
        text = text.replace(i, j)
    return text


def calculate_pages(records: int, max_page_size: int) -> int:
    """Helper function to calculate how many pages in API you need to request for in order to get
    all required records, basing on maximum page size the API can handle.

    :param records: How many records you need to pull from API.
    :param max_page_size: Maximum page size the API can handle.
    :return: Number of pages required to request for all records.
    """
    if records <= max_page_size:
        return 1
    return 1 + calculate_pages(records - max_page_size, max_page_size)


def colour_picker(percentage: int) -> discord.Colour:
    """Helper function to return discord.py Colour object based on provided value.\n
    percentage < 25 -> returns light grey\n
    25 < percentage < 50 -> returns green\n
    50 < percentage < 75 -> returns blue\n
    percentage >= 75 -> returns gold\n

    :param percentage: Value that determines what colour will be returned.
    :return: Calculated colour.
    """
    if percentage < 25:
        return discord.Colour.light_grey()
    if 25 <= percentage < 50:
        return discord.Colour.green()
    if 50 <= percentage < 75:
        return discord.Colour.blue()
    return discord.Colour.gold()

import logging
from typing import List

import discord
import yaml


def replace_all(text: str, replace_dict: dict) -> str:
    """Helper function to replace multiple character in a string.

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
    elif 25 <= percentage < 50:
        return discord.Colour.green()
    elif 50 <= percentage < 75:
        return discord.Colour.blue()
    else:
        return discord.Colour.gold()


def update_guild_config(filename: str,
                        guild: discord.Guild,
                        category: discord.CategoryChannel,
                        channels: List[discord.TextChannel],
                        auto: bool = None,
                        time: int = None):
    with open(filename, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        guild_config = {
            guild.id: {
                'category': category.id,
                'channels': {channel.name: channel.id for channel in channels},
                'auto': auto if auto else config[guild.id]['auto'],
                'time': time if time else config[guild.id]['time']
            }
        }
        if config:
            config.update(guild_config)
        else:
            config = guild_config
    with open(filename, 'w') as f:
        yaml.safe_dump(config, stream=f)
        logging.info(f'Updated config.yaml for guild {guild.name}')
    return config

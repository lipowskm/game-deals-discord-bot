import random
from dataclasses import dataclass
from typing import List

import aiohttp
import discord

import settings
from utils import calculate_pages, colour_picker, replace_all


class NoDealsFound(Exception):
    """Exception to raise when no deals are found in the API.
    """


@dataclass
class Deal:
    """A class to represent a deal.

    To create a Deal object, record from the API has to be passed in the constructor.

    Attributes
    ----------
    title : str
        title of the game on discount
    store_id : str
        ID of the store, that the game is available for purchase in, used by the API
    sale_price : float
        price of the game after discount
    normal_price : float
        normal price of the game
    saved_percentage : int
        how many percent is the price lowered
    saved_amount : int
        how much is the price lowered
    metacritic_score : str
        numeric score of the game on https://www.metacritic.com/
    steam_reviews_percent : str
        percentage of positive reviews on Steam
    steam_reviews_count : str
        amount of positive reviews on Steam
    steam_app_id : str
        ID of the game on Steam
    thumbnail_url : str
        url of the game thumbnail in .jpg format
    """

    def __init__(self, **attrs):
        self.title: str = attrs.pop('title', None)
        self.store_id: str = attrs.pop('storeID', None)
        self.sale_price = float(attrs.pop('salePrice', 0))
        self.normal_price = float(attrs.pop('normalPrice', 0))
        self.saved_percentage = round(float(attrs.pop('savings', 0)))
        self.metacritic_score: str = attrs.pop('metacriticScore', None)
        self.steam_reviews_percent: str = attrs.pop('steamRatingPercent', None)
        self.steam_reviews_count: str = attrs.pop('steamRatingCount', None)
        self.steam_app_id: str = attrs.pop('steamAppID', None)
        self.thumbnail_url: str = attrs.pop('thumb', None)

    def saved_amount(self) -> float:
        return round(self.normal_price - self.sale_price, 2)


async def get_deals(store: str = 'all',
                    amount: int = 60,
                    sort_by: str = 'Metacritic',
                    min_price: int = None,
                    max_price: int = 60,
                    min_steam_rating: int = None,
                    aaa: bool = False) -> List[Deal]:
    """Fetch deals from API basing on given parameters.

    :param store: Store name passed as string. Available options: 'steam', 'gog', 'all'.
    :param amount: Amount of deals returned in the list.
    :param sort_by: Specifies sorting criteria in the API.
    :param min_price: Minimum discount price of the deals.
    :param max_price: Maximum discount price of the deals.
    :param min_steam_rating: Minimum steam rating of the deals.
    :param aaa: If True, returns only deals with retail price more than 29$.
    :return: List of deals as a Deal class objects.
    :raises ValueError: When store parameter passed inside the function is not one of the possible options.
    :raises NoDealsFound: When no deals are found with given parameters.
    """
    if store not in settings.STORES_MAPPING.keys():
        raise ValueError('store must be one of %r.' % settings.STORES_MAPPING.keys())

    url = f'{settings.API_BASE_URL}' \
          f'?storeID={settings.STORES_MAPPING[store]}' \
          f'&sortBy={sort_by}' \
          f'&upperPrice={max_price}' \
          f'&onSale=1' \
          f'&pageSize=60' \
          f'&pageNumber=0'
    if min_price:
        url += f'&lowerPrice={min_price}'
    if min_steam_rating:
        url += f'&steamRating={min_steam_rating}'
    if aaa:
        url += '&AAA=1'

    pages = calculate_pages(amount, 60)
    session = aiohttp.ClientSession()
    deals_list: List[Deal] = []

    for e in range(0, pages):
        response = await session.get(url)
        response_list = await response.json()
        if len(response_list) == 0:
            if e == 0:
                await session.close()
                raise NoDealsFound('No deals found from provided API filters')
        for i, record in enumerate(response_list):
            if 60 > amount == i:
                break
            deal = Deal(**record)
            deals_list.append(deal)
        url = url.replace(f'&pageNumber={e}', f'&pageNumber={e + 1}')
        amount = amount - 60
    await session.close()
    return deals_list


async def get_random_deal(min_price: int = None,
                          retry_count: int = 5) -> Deal:
    """Fetch random deal from API.

    This returns only a deal that is available only in either Steam or GOG.

    :param min_price: Minimum discount price of the deal.
    :param retry_count: How many iterations to make in order to find the deal.
    :return: List of deals as a Deal class objects.
    :raises NoDealsFound: When no random deal is found.
    """
    url = f'{settings.API_BASE_URL}' \
          f'?storeID=1,7' \
          f'&sortBy=Metacritic' \
          f'&onSale=1' \
          f'&pageSize=1' \
          f'&pageNumber={random.randint(0, 1000)}'
    if min_price:
        url += f'&lowerPrice={min_price}'

    async with aiohttp.ClientSession() as session:
        for i in range(0, retry_count):
            if i + 1 == retry_count:
                raise NoDealsFound
            async with session.get(url) as response:
                response_list = await response.json()
                if len(response_list) == 0:
                    continue
                record = response_list[0]
                deal = Deal(**record)
                return deal


def get_embed_from_deal(deal: Deal) -> discord.Embed:
    """Function that takes a Deal class object as input parameter and converts it into discord.py Embed object.

    :param deal: Deal dataclass object.
    :return: discord.py Embed class object.
    """
    if deal.store_id == '1':
        deal_url = f'https://store.steampowered.com/app/{deal.steam_app_id}'
    else:
        replace_dict = {
            ' - ': ' ',
            "'": '',
            '.': '',
            ':': '',
            ' ': '_'
        }
        formatted_title = replace_all(deal.title, replace_dict).lower()
        deal_url = f'https://www.gog.com/game/{formatted_title}'
    embed = discord.Embed(title=deal.title,
                          description=f"*Sale price:* **{deal.sale_price}$**\n"
                                      f"*Normal price:* **{deal.normal_price}$**\n"
                                      f"*You save*: **{deal.saved_amount()}$ ({deal.saved_percentage}% off)**\n\n"
                                      f"*Steam reviews:* **{deal.steam_reviews_count}** "
                                      f"*({deal.steam_reviews_percent}% positive)*\n"
                                      f"*Link:* {deal_url}/",
                          colour=colour_picker(deal.saved_percentage))
    embed.set_image(url=deal.thumbnail_url)
    return embed

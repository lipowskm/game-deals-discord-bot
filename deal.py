from typing import List

import aiohttp
import discord
import random
import settings

from utils import calculate_pages, colour_picker, replace_all


class NoDealsFound(Exception):
    """

    Exception handling when no deals are found in the API.
    """
    pass


class Deal:
    def __init__(self, record: dict):
        self.title = record['title']
        self.store_id = record['storeID']
        self.sale_price = float(record['salePrice'])
        self.normal_price = float(record['normalPrice'])
        self.saved_percentage = round(float(record['savings']))
        self.saved_amount = round(float(self.normal_price) - float(self.sale_price), 2)
        self.metacritic_score = int(record['metacriticScore'])
        self.steam_reviews_percent = int(record['steamRatingPercent'])
        self.steam_reviews_count = int(record['steamRatingCount'])
        self.steam_app_id = record['steamAppID']
        self.thumbnail_url = record['thumb']


stores_mapping = {
    'steam': '1',
    'gog': '7',
    'all': '1,7'
}


async def get_deals(store: str = 'all',
                    amount: int = 60,
                    sort_by: str = 'Metacritic',
                    min_price: int = None,
                    max_price: int = 60,
                    min_steam_rating: int = None,
                    aaa: bool = False) -> List[Deal]:
    url = f'{settings.API_BASE_URL}' \
          f'?storeID={stores_mapping[store]}' \
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
        url += f'&AAA=1'

    pages = calculate_pages(amount, 60)
    session = aiohttp.ClientSession()
    deals_list: List[Deal] = []

    for e in range(0, pages):
        request = await session.get(url)
        response_list = await request.json()
        if len(response_list) == 0:
            if e == 0:
                await session.close()
                raise NoDealsFound('No deals found from provided API filters')
            else:
                break
        for i, record in enumerate(response_list):
            if 60 > amount == i:
                break
            deal = Deal(record)
            deals_list.append(deal)
        url = url.replace(f'&pageNumber={e}', f'&pageNumber={e + 1}')
        amount = amount - 60
    await session.close()
    return deals_list


async def get_random_deal(min_price: int = None) -> Deal:
    url = f'https://www.cheapshark.com/api/1.0/deals' \
          f'?storeID=1,7' \
          f'&sortBy=Metacritic' \
          f'&onSale=1' \
          f'&pageSize=1' \
          f'&pageNumber={random.randint(0, 1000)}'
    if min_price:
        url += f'&lowerPrice={min_price}'

    session = aiohttp.ClientSession()

    while True:
        request = await session.get(url)
        if (response_list := await request.json()) is None:
            continue
        record = response_list[0]
        deal = Deal(record)
        await session.close()
        return deal


def get_embed_from_deal(deal: Deal) -> discord.Embed:
    if deal.store_id == '1':
        link = f'https://store.steampowered.com/app/{deal.steam_app_id}'
    else:
        replace_dict = {
            ' - ': ' ',
            "'": '',
            '.': '',
            ':': '',
            ' ': '_'
        }
        formatted_title = replace_all(deal.title, replace_dict).lower()
        link = f'https://www.gog.com/game/{formatted_title}'
    embed = discord.Embed(title=deal.title,
                          description=f"*Sale price:* **{deal.sale_price}$**\n"
                                      f"*Normal price:* **{deal.normal_price}$**\n"
                                      f"*You save*: **{deal.saved_amount}$ ({deal.saved_percentage}% off)**\n\n"
                                      f"*Steam reviews:* **{deal.steam_reviews_count}** "
                                      f"*({deal.steam_reviews_percent}% positive)*\n"
                                      f"*Link:* {link}/",
                          colour=colour_picker(deal.saved_percentage))
    embed.set_image(url=deal.thumbnail_url)
    return embed

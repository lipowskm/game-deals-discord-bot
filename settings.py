from decouple import config

API_BASE_URL = config('API_BASE_URL')
DATABASE_URL = config('DATABASE_URL')
BOT_TOKEN = config('BOT_TOKEN')
PREFIX = config('PREFIX')

CATEGORY = config('CATEGORY')
STEAM_CHANNEL = config('STEAM_CHANNEL')
STEAM_AAA_CHANNEL = config('STEAM_AAA_CHANNEL')
STEAM_DEALS_AMOUNT = int(config('STEAM_DEALS_AMOUNT'))
GOG_CHANNEL = config('GOG_CHANNEL')
GOG_AAA_CHANNEL = config('GOG_AAA_CHANNEL')
GOG_DEALS_AMOUNT = int(config('GOG_DEALS_AMOUNT'))

CHANNELS_SETTINGS = {
    STEAM_CHANNEL: {
        'min_retail_price': 0,
        'max_retail_price': 29,
        'store': 'steam'
    },
    STEAM_AAA_CHANNEL: {
        'min_retail_price': 29,
        'max_retail_price': 1000,
        'store': 'steam'
    },
    GOG_CHANNEL: {
        'min_retail_price': 0,
        'max_retail_price': 29,
        'store': 'gog'
    },
    GOG_AAA_CHANNEL: {
        'min_retail_price': 29,
        'max_retail_price': 1000,
        'store': 'gog'
    }
}

STORES_MAPPING = {
    'steam': '1',
    'gog': '7',
    'all': '1,7'
}

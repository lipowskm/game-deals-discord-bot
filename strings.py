import settings

COMMAND_UPDATE_BRIEF = 'Updates specific store channel'
COMMAND_UPDATE_DESC = ('Updates specific store channel with amount of deals specified by user.\n\n'
                       'If no arguments provided, updates all stores with 60 positions\n\n'
                       "<store> - optional, available options: [steam, gog, all].\n"
                       '[deals_amount] - optional, integer between 1 and 100. Default value is 60.\n\n'
                       'Examples:\n'
                       f'{settings.PREFIX} update steam 10\n'
                       f'{settings.PREFIX} update 60')

COMMAND_RANDOM_BRIEF = 'Posts random deal in current channel'
COMMAND_RANDOM_DESC = ('Posts random deal in current channel.\n\n'
                       'Example:\n'
                       f'{settings.PREFIX} random')

COMMAND_FLIP_BRIEF = 'Posts a flipbook of deals in current channel'
COMMAND_FLIP_DESC = ('Posts flipbook of deals in current channel.\n\n'
                     'Flipbook is assigned to the user who requested for it, so only he '
                     'can interact with it.\n\n'
                     "[min_price] - optional, if specified will only post games "
                     "with discount price (USD) higher than specified amount. Default is 0.\n"
                     "[max_price] - optional, if specified will only post games "
                     "with discount price (USD) lower than specified amount. Default is 60.\n\n"
                     'Example:\n'
                     f'{settings.PREFIX} flip 10 -> returns deals with minimum discount price of 10 USD\n'
                     f'{settings.PREFIX} flip 5 20 -> returns deals with minimum discount price of 5 USD '
                     f'and maximum discount price of 20 USD')

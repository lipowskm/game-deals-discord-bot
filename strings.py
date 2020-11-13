import settings

COMMAND_UPDATE_BRIEF = 'Update specific store channel'
COMMAND_UPDATE_DESC = f"""Update specific store channel with amount of deals specified by user.

                          If no arguments provided, updates all stores with 60 positions.

                          <store> - optional, available options: [steam, gog, all]
                          [deals_amount] - optional, integer between 1 and 100. Default value is 60.

                          Examples:
                          {settings.PREFIX} update steam 10\n
                          {settings.PREFIX} update 60"""

COMMAND_RANDOM_BRIEF = 'Post random deal in current channel'
COMMAND_RANDOM_DESC = f"""Post random deal in current channel.

                          Example:
                          {settings.PREFIX} random"""

COMMAND_FLIP_BRIEF = 'Post a flipbook of deals in current channel'
COMMAND_FLIP_DESC = ('Post flipbook of deals in current channel.\n\n'
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

COMMAND_AUTO_BRIEF = 'Setup automatic update'
COMMAND_AUTO_DESC = """Command group to manage settings for the automatic update of deals.
                       Deals are provided every day at specified hour. Default is 12:00 UTC"""

COMMAND_ENABLE_BRIEF = 'Enable automatic updates'
COMMAND_ENABLE_DESC = 'Enable automatic updates of deals.'

COMMAND_DISABLE_BRIEF = 'Disable automatic updates'
COMMAND_DISABLE_DESC = 'Disable automatic updates of deals.'

COMMAND_TIME_BRIEF = 'Set hour of the day when the deals are going to be sent.'
COMMAND_TIME_DESC = ('Set hour of the day when the deals are going to be sent.\n'
                     'If no argument is provided, bot returns which hour is currently set.\n\n'
                     '[hour] - optional, if specified will set hour of deals delivery to specified amount. '
                     'Possible values: 0 - 23\n'
                     'Default is 12:00 UTC.\n\n'
                     'Example:\n'
                     f'{settings.PREFIX} auto time\n'
                     f'{settings.PREFIX} auto time 18')

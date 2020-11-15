# Game Deals Discord Bot

[![BotLink](https://img.shields.io/badge/Discord-Invite%20bot%20to%20your%20server-blue?style=plastic&logo=discord)](https://discord.com/api/oauth2/authorize?client_id=773196224975077437&permissions=268445728&scope=bot)

## Description

This is yet another bot for Discord that tracks deals for games. Unlike the other ones that are available, this one operates differently.

The main priority in creating this bot was to minimize effort the user has to make, so for the most part the bot handles things by itself, but it doesn't mean, that there aren't any commands available!

It has it's own schedule, so everyday at the same hour (between 12:00 UTC and 13:00 UTC) it cleans the channels and posts new deals there. That way anyone who enters the channel will only see deals that are still available for purchase. The time can be changed by server administrator.

<p align="center">
  <img src=https://i.imgur.com/c7xNGn8.gif width="480" height="480">
</p>

Because Discord is somewhat of a limited frontend, the bot is also limited in amount of deals it can display. That's why it posts deals sorted by [Metacritic](https://www.metacritic.com) rating, so the user always sees the best possible deals.

### Built With
* [Python](https://www.python.org)
* [PostgreSQL] (https://www.postgresql.org)
* [discord.py](https://pypi.org/project/discord.py)
* [SQLAlchemy] (https://www.sqlalchemy.org)
* [aiohttp](https://pypi.org/project/aiohttp)
* [databases] (https://pypi.org/project/databases)
* [CheapShark API](https://apidocs.cheapshark.com)

## How to use

After inviting the bot to the server, it will automatically create required channels that are only available to it (so the other users can't send any messages there) and starts posting the deals there. After that deals will be updated every day at the same hour. 

For the commands use `!gd` prefix followed by a space. Example: `!gd help`. 

You are free to rename the channels as you wish, and if you happen to delete one of them by mistake, don't worry, because the bot will create a new one automatically.

It is **highly recommended** to mute the category which the channels are assigned to, since the bot is spamming them a lot.

### Available commands

| Command | Subcommand | Arguments               | Required permissions | Description                                                                                                                                                                                                                                                                                                                                                    |
|---------|------------|-------------------------|----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| update  |            | *[store]* *[deals_amount]*  | Administrator        | Update specific store channel with amount of deals specified by user. <br/> If no arguments provided, updates all stores with 60 deals. <br/><br/>  *[store]* - optional, can be either steam, gog or all. Default is all. <br/> *[deals_amount]* - optional, amount of deals to send across all channels. Default is 60. Maximum value is 200. |
| random  |            | *[min_price]*             |                      | Posts random deal in the channel, which the command has been invoked in. <br/><br/> *[min_price]* - optional, minimal sale price of the deal.                                                                                                                                                                                                                    |
| flip    |            | *[min_price]* *[max_price]* |                      | Posts a flipbook of deals in the channel, which the command has been invoked in. <br/> Flipbook is assigned to the user that requested for it, so only he can interact with it. <br/><br/> *[min_price]* - optional, minimal sale price of deals in flipbook. <br/> *[max_price]* - optional, maximum sale price of deals in flipbook.                             |
| auto    | enable     |                         | Administrator        | Enables daily delivery of deals in proper channels.                                                                                                                                                                                                                                                                                                            |
| auto    | disable    |                         | Administrator        | Disables daily delivery of deals in proper channels.                                                                                                                                                                                                                                                                                                           |
| auto    | time       | *[hour]*                  | Administrator        | Informs about the set up hour of the day that the deals are going to be sent at. <br/> Also changes the hour if proper argument is provided. <br/><br/>  *[hour]* - optional, must be an integer between 0 and 23. <br/>  If specified, bot will change the hour of delivery (UTC format) on the server. Default is 12:00 UTC.                                   |
| help    |            | *[command_name]*          |                      | Get information about available commands or how to use them.                                                                                                                                                                                                                                                                                                   

## Examples

### Flip command
<img src=https://i.imgur.com/ZuYLZEl.gif width="480" height="326">

### Random command
<img src=https://i.imgur.com/mivYnRt.gif width="480" height="326">

from slashcommands import *
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

bot.run(bot_parameters.TOKEN)

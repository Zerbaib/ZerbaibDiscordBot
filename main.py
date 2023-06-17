import disnake
from disnake.ext import commands
import platform
import os
import json

# Charger les informations de configuration depuis config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Créer une instance de bot
intents = disnake.Intents.default()

bot = commands.InteractionBot(intents=intents)

@bot.event
async def on_ready():
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    print('===============================================')
    print("The bot is ready!")
    print(f'Logged in as {bot.user.name}#{bot.user.discriminator} | {bot.user.id}')
    print(f'Running on {platform.system()} {platform.release()} ({os.name})')
    print(f'Bot version: {config.get("bot_version", "")}')
    print(f"Disnake version : {disnake.__version__}")
    print(f"Python version: {platform.python_version()}")
    print('===============================================')

    # Charger les autres cogs depuis le dossier "cogs"
    for extension in config['extensions']:
        name = extension['name']
        enabled = extension['enabled']

        if enabled:
            try:
                bot.load_extension(f'cogs.{name}')
                print(f'Cog chargé : {name}')
            except Exception as e:
                print(f'Erreur lors du chargement du cog {name} : {str(e)}')
        else:
            print(f'Cog désactivé : {name}')


# Lancer le bot
bot.run(config['token'])

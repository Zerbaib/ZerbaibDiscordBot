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
intents.message_content = False  # Désactiver la récupération du contenu des messages
intents.members = True

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

    # Charger le cog StatusCog
    try:
        bot.load_extension('cogs.status')
        print('Cog chargé : status')
    except Exception as e:
        print(f'Erreur lors du chargement du cog status : {str(e)}')

    # Charger les autres cogs depuis le dossier "cogs"
    for extension in config['extensions']:
        if extension != 'status':
            try:
                bot.load_extension(f'cogs.{extension}')
                print(f'Cog chargé : {extension}')
            except Exception as e:
                print(f'Erreur lors du chargement du cog {extension} : {str(e)}')

# Lancer le bot
bot.run(config['token'])

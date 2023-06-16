import disnake
from disnake.ext import commands
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
    print(f'Connecté en tant que {bot.user}')

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

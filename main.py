import disnake
from disnake.ext import commands
import json

# Charger les informations de configuration depuis config.json
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Créer une instance de bot
bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user}')

# Charger les cogs depuis le dossier "cogs"
if __name__ == '__main__':
    for extension in config['extensions']:
        try:
            bot.load_extension(f'cogs.{extension}')
            print(f'Cog chargé : {extension}')
        except Exception as e:
            print(f'Erreur lors du chargement du cog {extension}: {str(e)}')

# Lancer le bot
bot.run(config['token'])

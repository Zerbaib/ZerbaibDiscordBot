import disnake
from disnake.ext import commands
import json

class AutoRoleCog(commands.Cog):
    def __init__(self, bot, config_file):
        self.bot = bot
        self.config_file = config_file
        self.load_config()

    def load_config(self):
        with open(self.config_file, 'r') as file:
            self.config = json.load(file)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        roles = self.config.get('roles', {})

        for role_id in roles:
            role = guild.get_role(role_id)
            if role:
                await member.add_roles(role)

    @commands.Cog.listener()
    async def on_ready(self):
        print('AutoRole cog is ready!')

def setup(bot):
    config_file = 'config.json'  # Remplacez par le chemin vers votre fichier de configuration JSON
    bot.add_cog(AutoRoleCog(bot, config_file))

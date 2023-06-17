import disnake
from disnake.ext import commands
import json

class AutoRoleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "config/config.json"
        self.load_config()

    def load_config(self):
        with open(self.config_file, 'r') as file:
            self.config = json.load(file)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        roles = self.config.get('auto_roles', {})

        for role_id in roles:
            role = guild.get_role(role_id)
            if role:
                await member.add_roles(role)

    @commands.Cog.listener()
    async def on_ready(self):
        print('AutoRole cog is ready!')

def setup(bot):
    bot.add_cog(AutoRoleCog(bot))

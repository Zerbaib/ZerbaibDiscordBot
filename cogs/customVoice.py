import disnake
from disnake.ext import commands
import json
import asyncio

class CustomVoiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_path = 'config.json'
        self.load_config()

    def load_config(self):
        with open(self.config_path, 'r') as config_file:
            self.config = json.load(config_file)

    async def delete_temporary_channel(self, channel):
        await asyncio.sleep(3)  # Wait for 3 seconds
        if channel:
            await channel.delete()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel and after.channel.id == self.config.get('target_channel_id'):
            guild = member.guild
            category = after.channel.category  # Get the category of the joined channel
            overwrites = {
                guild.default_role: disnake.PermissionOverwrite(connect=False),
                member: disnake.PermissionOverwrite(connect=True)
            }

            channel = await guild.create_voice_channel(name=member.name, overwrites=overwrites, category=category)

            await member.move_to(channel)

            self.bot.loop.create_task(self.delete_temporary_channel(channel))

    @commands.Cog.listener()
    async def on_ready(self):
        print('CustomVoice cog is ready!')

def setup(bot):
    bot.add_cog(CustomVoiceCog(bot))

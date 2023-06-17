import disnake
from disnake.ext import commands
import random
import asyncio
import json

class StatusCog(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.update_status())

    async def update_status(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            guild = self.bot.get_guild(self.config.get('server_id'))
            if guild:
                member_count = len(guild.members)
            else:
                member_count = 0

            status_message = random.choice(self.config.get('status_messages'))
            status_message = status_message.replace('{member_count}', str(member_count))
            status_message = status_message.replace('{bot_version}', self.config.get('bot_version', ''))

            status_type = self.config.get('status_type')
            if status_type == 'watching':
                await self.bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.watching, name=status_message))
            elif status_type == 'playing':
                await self.bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.playing, name=status_message))
            elif status_type == 'custom':
                await self.bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.custom, name=status_message))

            await asyncio.sleep(self.config.get('status_interval'))

    @commands.Cog.listener()
    async def on_ready(self):
        print('Status cog is ready!')

def setup(bot):
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    bot.add_cog(StatusCog(bot, config))

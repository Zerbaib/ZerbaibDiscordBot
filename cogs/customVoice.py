import disnake
from disnake.ext import commands
import json
import asyncio

class CustomVoiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "config.json"
        self.temp_channels = {}
        self.load_config()

    def load_config(self):
        with open(self.config_file, 'r') as file:
            self.config = json.load(file)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        target_channel_id = self.config.get('target_channel_id')
        if after.channel and after.channel.id == target_channel_id:
            guild = member.guild
            category = after.channel.category
            overwrites = {
                guild.default_role: disnake.PermissionOverwrite(connect=False),
                member: disnake.PermissionOverwrite(connect=True)
            }

            channel = await guild.create_voice_channel(name=member.name, overwrites=overwrites, category=category)
            await member.move_to(channel)

            # Définir la limite de membre du canal vocal
            await channel.edit(user_limit=10)

            # Ajouter le canal vocal temporaire au dictionnaire avec le temps de création actuel
            self.temp_channels[channel.id] = asyncio.get_event_loop().time()

    async def delete_temporary_channels(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            current_time = asyncio.get_event_loop().time()

            # Parcourir les canaux vocaux temporaires et vérifier s'ils doivent être supprimés
            for channel_id, creation_time in list(self.temp_channels.items()):
                channel = self.bot.get_channel(channel_id)

                if not channel:
                    # Canal introuvable, le supprimer du dictionnaire
                    del self.temp_channels[channel_id]
                    continue

                # Vérifier si le canal est vide depuis plus de 3 secondes
                if len(channel.members) == 0 and current_time - creation_time >= 3:
                    await channel.delete()
                    del self.temp_channels[channel_id]

            await asyncio.sleep(1)  # Attendre 1 seconde avant de vérifier à nouveau

    @commands.Cog.listener()
    async def on_ready(self):
        print('CustomVoice cog is ready!')
        self.bot.loop.create_task(self.delete_temporary_channels())

def setup(bot):  # Remplacez par le chemin vers votre fichier de configuration JSON
    bot.add_cog(CustomVoiceCog(bot))

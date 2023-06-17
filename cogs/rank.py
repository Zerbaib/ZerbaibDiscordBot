import disnake
from disnake.ext import commands
import json
import os
import random

class RankCog(commands.Cog):
    def __init__(self, bot, embed_color, base_level, level_factor):
        self.bot = bot
        self.data_path = 'data/ranks.json'
        self.config_path = 'config.json'
        self.embed_color = embed_color
        self.base_level = base_level
        self.level_factor = level_factor
        self.load_data()
        self.load_config()

    def load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, 'r') as data_file:
                self.ranks = json.load(data_file)
        else:
            self.ranks = {}

    def save_data(self):
        with open(self.data_path, 'w') as data_file:
            json.dump(self.ranks, data_file, indent=4)

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as config_file:
                self.config = json.load(config_file)
        else:
            self.config = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        user_id = str(message.author.id)
        if user_id not in self.ranks:
            self.ranks[user_id] = {"xp": 0, "level": 0}

        self.ranks[user_id]["xp"] += random.randint(1, 5)
        xp = self.ranks[user_id]["xp"]
        lvl = self.ranks[user_id]["level"]

        xp_required = 5 * (lvl ** 2) + 10 * lvl + 10

        if xp >= xp_required:
            lvl = lvl + 1
            self.ranks[user_id]["level"] = lvl
            self.ranks[user_id]["xp"] = lvl
            self.save_data()
            await self.check_level_roles(message.author, lvl)  # Vérifier les rôles pour le niveau atteint
            xp_required = 5 * (lvl ** 2) + 10 * lvl + 10
            embed = disnake.Embed(
                title=f'Congratulations, {message.author.name}!',
                description=f'**You reached level **```{lvl}```\n*You need ``{xp_required}`` xp for the next level*',
                color=self.embed_color
            )
            msg = await message.channel.send(embed=embed)
            await msg.delete(delay=5)  # Supprimer le message après 5 secondes

        self.save_data()

    async def check_level_roles(self, user, level):
        if 'level_roles' in self.config:
            for level_threshold, role_id in self.config['level_roles'].items():
                if level >= int(level_threshold):
                    role = user.guild.get_role(role_id)
                    if role:
                        await user.add_roles(role)

    @commands.slash_command(name='rank', description='Displays your current rank or the rank of a user')
    async def rank(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User = None):
        if user is None:
            user_id = str(inter.author.id)
            user_name = str(inter.author.name)
        else:
            user_id = str(user.id)
            user_name = str(user)
        
        if user_id in self.ranks:
            xp = self.ranks[user_id]["xp"]
            level = self.ranks[user_id]["level"]
            xp_required = 5 * (level ** 2) + 10 * level + 10
            embed = disnake.Embed(
                title=f"{user_name}'s rank -> #{self.get_user_rank(user_id)}",
                description=f'**Level:** ```{level}```\n**XP:** ``{xp}``\n*Need* ``{xp_required}`` *to win one level*',
                color=self.embed_color
            )

            await inter.response.send_message(embed=embed)
        else:
            await inter.response.send_message(f'{user_name} does not have a rank yet.')

    @commands.slash_command(name='leaderboard', description='Displays the top 10 leaderboard')
    async def leaderboard(self, inter: disnake.ApplicationCommandInteraction):
        sorted_ranks = sorted(self.ranks.items(), key=lambda x: x[1]["xp"], reverse=True)
        
        embed = disnake.Embed(
            title='Top 10 Leaderboard',
            color=self.embed_color
        )

        for i, (user_id, data) in enumerate(sorted_ranks[:10]):
            user = await self.bot.fetch_user(int(user_id))
            if user is None:
                user_name = f'Unknown User ({user_id})'
            else:
                user_name = str(user)

            xp = data["xp"]
            level = data["level"]

            embed.add_field(name=f'{i+1}. {user_name}', value=f'Level: ``{level}``\nXP: ``{xp}``', inline=False)

        await inter.response.send_message(embed=embed)

    def get_user_rank(self, user_id):
        sorted_ranks = sorted(self.ranks.items(), key=lambda x: x[1]["xp"], reverse=True)
        for i, (id, _) in enumerate(sorted_ranks):
            if id == user_id:
                return i+1

        return -1

    @commands.Cog.listener()
    async def on_ready(self):
        print('Rank cog is ready!')

def setup(bot):
    bot.add_cog(RankCog(bot, embed_color=0x00ff00, base_level=1, level_factor=0.1))

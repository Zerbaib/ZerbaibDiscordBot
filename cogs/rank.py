import disnake
from disnake.ext import commands
import json
import os

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

    def save_config(self):
        with open(self.config_path, 'w') as config_file:
            json.dump(self.config, config_file, indent=4)

    def calculate_level(self, xp):
        return self.base_level + int(xp / 10)

    def calculate_next_level_xp(self, current_xp):
        current_level = self.calculate_level(current_xp)
        next_level = current_level + 1
        next_level_xp = self.base_level + (next_level - self.base_level) * 2
        return int(next_level_xp)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        user_id = str(message.author.id)
        if user_id not in self.ranks:
            self.ranks[user_id] = {"xp": 0, "level": 0}

        self.ranks[user_id]["xp"] += 1
        level = self.calculate_level(self.ranks[user_id]["xp"])
        if level > self.ranks[user_id]["level"]:
            self.ranks[user_id]["level"] = level
            await self.check_level_roles(message.author, level)  # Vérifier les rôles pour le niveau atteint
            
            next_level_xp = self.calculate_next_level_xp(self.ranks[user_id]["xp"])
            countdown = next_level_xp - self.ranks[user_id]["xp"]
            
            embed = disnake.Embed(
                title=f'Congratulations, {message.author.name}!',
                description=f'You reached level {level}!\n\nNext Level: {countdown} XP remaining',
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
            next_level_xp = self.calculate_next_level_xp(xp)
            countdown = next_level_xp - xp

            embed = disnake.Embed(
                title=f"{user_name}'s rank -> #{self.get_user_rank(user_id)}",
                description=f'**Level:** ```{level}```\n**XP:** ``{xp}``\n\nNext Level: {countdown} XP remaining',
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
        print('RankCog cog is ready!')

def setup(bot):
    bot.add_cog(RankCog(bot, embed_color=0x00ff00, base_level=0, level_factor=0.1))

import disnake
from disnake.ext import commands
import json
import os

class RankCog(commands.Cog):
    def __init__(self, bot, embed_color, base_level, level_factor):
        self.bot = bot
        self.data_path = 'data/ranks.json'
        self.embed_color = embed_color  # Utiliser la couleur personnalisée
        self.base_level = base_level
        self.level_factor = level_factor
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_path):
            with open(self.data_path, 'r') as data_file:
                self.ranks = json.load(data_file)
        else:
            self.ranks = {}

    def save_data(self):
        with open(self.data_path, 'w') as data_file:
            json.dump(self.ranks, data_file, indent=4)

    def calculate_level(self, xp):
        return self.base_level + int((xp ** self.level_factor) / 100)

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
            await message.channel.send(f'Congratulations, {message.author.mention}! You reached level {level}!')

        self.save_data()

    @commands.slash_command(name='rank', description='Displays your current rank or the rank of a user')
    async def rank(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User = None):
        if user is None:
            user_id = str(inter.author.id)
            user_name = str(inter.author)
        else:
            user_id = str(user.id)
            user_name = str(user)
        
        if user_id in self.ranks:
            xp = self.ranks[user_id]["xp"]
            level = self.ranks[user_id]["level"]

            embed = disnake.Embed(
                title=f'{user_name} is rank #{self.get_user_rank(user_id)}',
                description=f'Level: {level}\nXP: {xp}',
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
            user = self.bot.get_user(int(user_id))
            if user is None:
                user_name = f'Unknown User ({user_id})'
            else:
                user_name = str(user)

            xp = data["xp"]
            level = data["level"]

            embed.add_field(name=f'{i+1}. {user_name}', value=f'Level: {level}\nXP: {xp}', inline=False)

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
    bot.add_cog(RankCog(bot, embed_color=0x00ff00, base_level=1, level_factor=0.1))
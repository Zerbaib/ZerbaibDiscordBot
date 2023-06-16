import disnake
from disnake.ext import commands
import json
import os
from operator import itemgetter

class RankCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data_path = 'data/ranks.json'
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

    @commands.slash_command(name='rank', description='Displays your current rank or the rank of a user')
    async def rank(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User = None):
        if user is None:
            user_id = str(inter.author.id)
            user_name = str(inter.author)
        else:
            user_id = str(user.id)
            user_name = str(user)
        
        if user_id in self.ranks:
            rank = self.ranks[user_id]

            embed = disnake.Embed(
                title='Rank',
                description=f'The rank of {user_name} is: {rank}',
                color=0x00ff00
            )

            await inter.response.send_message(embed=embed)
        else:
            await inter.response.send_message(f'{user_name} does not have a rank yet.')

    @commands.slash_command(name='leaderboard', description='Displays the top 10 leaderboard')
    async def leaderboard(self, inter: disnake.ApplicationCommandInteraction):
        sorted_ranks = sorted(self.ranks.items(), key=itemgetter(1), reverse=True)
        
        embed = disnake.Embed(
            title='Top 10 Leaderboard',
            color=0x00ff00
        )

        for i, (user_id, rank) in enumerate(sorted_ranks[:10]):
            user = self.bot.get_user(int(user_id))
            if user is None:
                user_name = f'Unknown User ({user_id})'
            else:
                user_name = str(user)

            embed.add_field(name=f'{i+1}. {user_name}', value=f'Rank: {rank}', inline=False)

        await inter.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(RankCog(bot))

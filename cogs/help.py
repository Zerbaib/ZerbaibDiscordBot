import disnake
from disnake.ext import commands
import json

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name='help',
        description='Displays the list of available commands by cog',
        options=[
            disnake.Option(
                type=3,
                name='cog',
                description='The cog to display commands for',
                required=True,
                choices=[
                    disnake.OptionChoice(name=cog, value=cog) for cog in config['extensions'] if cog != 'help'
                ]
            )
        ]
    )
    async def help_command(self, inter, cog: str):
        cog_name = cog.capitalize() + 'Cog'
        if cog_name not in self.bot.cogs:
            await inter.response.send_message('This cog does not exist.')
            return

        cog_obj = self.bot.get_cog(cog_name)
        commands = cog_obj.get_commands()

        if not commands:
            await inter.response.send_message('This cog doesn\'t have commands.')
            return

        embed = disnake.Embed(title=f'Commands in {cog_name}', color=disnake.Color.blurple())
        for command in commands:
            embed.add_field(name=command.name, value=command.description, inline=False)

        await inter.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        print('Help cog is ready!')

def setup(bot):
    bot.add_cog(HelpCog(bot))

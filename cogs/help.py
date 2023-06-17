import disnake
from disnake.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(
        name='help',
        description='Displays the list of available commands by category',
        options=[
            disnake.Option(
                name='category',
                description='The category of commands to display',
                type=disnake.OptionType.STRING,
                required=False
            )
        ]
    )
    async def help_command(self, inter, category: str = None):
        if category is None:
            # Display the list of categories
            categories = [cog.qualified_name for cog in self.bot.cogs.values()]
            category_list = '\n'.join(f'`{category}`' for category in categories)
            embed = disnake.Embed(
                title='List of Categories',
                description=category_list,
                color=disnake.Color.blurple()
            )
            await inter.response.send_message(embed=embed)
        else:
            # Display the commands of a specific category
            category_cog = self.bot.get_cog(category)
            if category_cog is None:
                embed = disnake.Embed(
                    title='Error',
                    description=f'The category "{category}" does not exist',
                    color=disnake.Color.red()
                )
                await inter.response.send_message(embed=embed)
            else:
                command_list = []
                for command in category_cog.get_commands():
                    command_info = f'`{command.name}`: {command.description}\n'
                    command_list.append(command_info)
                commands_info = '\n'.join(command_list)
                embed = disnake.Embed(
                    title=f'Commands in category "{category}"',
                    description=commands_info,
                    color=disnake.Color.blurple()
                )
                await inter.response.send_message(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        print('Help cog is ready!')

def setup(bot):
    bot.add_cog(HelpCog(bot))
import disnake
from disnake.ext import commands
import json

class RoleMenuCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config()
        self.rmenu = self.load_rconfig()
        self.role_menus = {}

    def load_rconfig(self):
        with open('config/rolemenue.json', 'r') as config_file:
            return json.load(config_file)

    def load_config(self):
        with open('config/config.json', 'r') as config_file:
            return json.load(config_file)

    def save_rconfig(self):
        with open('config/rolemenue.json', 'w') as config_file:
            json.dump(self.rmenu, config_file, indent=4)

    def save_config(self):
        with open('config/config.json', 'w') as config_file:
            json.dump(self.config, config_file, indent=4)

    async def create_role_menu(self, channel_id, title, description, options):
        channel = self.bot.get_channel(channel_id)
        if not channel:
            print(f'Invalid channel ID: {channel_id}')
            return

        view = disnake.ui.View()
        for option in options:
            view.add_item(disnake.ui.Button(style=disnake.ButtonStyle.secondary, label=option['label'], custom_id=option['value']))

        embed = disnake.Embed(title=title, description=description)
        message = await channel.send(embed=embed, view=view)

        self.role_menus[message.id] = {
            'channel_id': channel_id,
            'message_id': message.id,
            'options': options
        }

    @commands.Cog.listener()
    async def on_ready(self):
        print('Role Menu cog is ready!')

        for menu in self.rmenu['role_menus']:
            channel_id = menu['channel_id']
            title = menu['title']
            description = menu['description']
            options = menu['options']
            await self.create_role_menu(channel_id, title, description, options)

    @commands.Cog.listener()
    async def on_button_click(self, inter):
        if not isinstance(inter, disnake.ButtonInteraction):
            return

        if inter.message.id not in self.role_menus:
            return

        menu = self.role_menus[inter.message.id]
        selected_option = next((option for option in menu['options'] if option['value'] == inter.component.custom_id), None)
        if not selected_option:
            return

        member = inter.guild.get_member(inter.author.id)
        role_id = selected_option['role_id']
        role = inter.guild.get_role(role_id)

        if role:
            if role in member.roles:
                await member.remove_roles(role)
                await inter.response.send_message(f'You have been removed from the role: {role.name}.', ephemeral=True)
            else:
                await member.add_roles(role)
                await inter.response.send_message(f'You have been added to the role: {role.name}.', ephemeral=True)

    @commands.slash_command(
        name='updateroles',
        description='Update the role menus',
    )
    async def update_role_menus(self, inter):
        self.role_menus = {}

        for menu in self.rmenu['role_menus']:
            channel_id = menu['channel_id']
            title = menu['title']
            description = menu['description']
            options = menu['options']
            await self.create_role_menu(channel_id, title, description, options)

        await inter.response.send_message('Role menus have been updated.')

def setup(bot):
    bot.add_cog(RoleMenuCog(bot))

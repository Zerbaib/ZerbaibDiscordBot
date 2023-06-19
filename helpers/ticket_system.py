import disnake
import asyncio
import json
import sqlite3
import datetime
import chat_exporter
import io
from disnake.ext import commands

with open("config/config.json", mode="r") as config_file:
    config = json.load(config_file)

with open("config/ticket.json", mode="r") as config_file:
    ticket = json.load(config_file)

GUILD_ID = config["server_id"] #Your Server ID aka Guild ID 
TICKET_CHANNEL = ticket["ticket_channel_id"] #Ticket Channel where the Bot should send the SelectMenu + Embed

CATEGORY_ID1 = ticket["category_id_1"] #Category 1 where the Bot should open the Ticket for the Ticket option 1
CATEGORY_ID2 = ticket["category_id_2"] #Category 2 where the Bot should open the Ticket for the Ticket option 2

TEAM_ROLE1 = ticket["team_role_id_1"] #Staff Team role id
TEAM_ROLE2 = ticket["team_role_id_2"] #Staff Team role id

LOG_CHANNEL = ticket["log_channel_id"] #Where the Bot should log everything 
TIMEZONE = config["timezone"]

conn = sqlite3.connect('data/ticket.db')
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS ticket 
           (id INTEGER PRIMARY KEY AUTOINCREMENT, discord_name TEXT, discord_id INTEGER, ticket_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
conn.commit()

class Ticket_System(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Bot Loaded | ticket_system.py ✅')
        self.bot.add_view(MyView(bot=self.bot))
        self.bot.add_view(CloseButton(bot=self.bot))
        self.bot.add_view(TicketOptions(bot=self.bot))

    #Closes the Connection to the Database when shutting down the Bot
    @commands.Cog.listener()
    async def on_bot_shutdown():
        cur.close()
        conn.close()

class MyView(disnake.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @disnake.ui.select(
        custom_id="support",
        placeholder="Choose a Ticket option",
        options=[
            disnake.SelectOption(
                label="Need help",  #Name of the 1 Select Menu Option
                description="If you have a problem with anything go here!",  #Description of the 1 Select Menu Option
                emoji="🧐",        #Emoji of the 1 Option  if you want a Custom Emoji read this  https://github.com/Simoneeeeeeee/Discord-Select-Menu-Ticket-Bot/tree/main#how-to-use-custom-emojis-from-your-discors-server-in-the-select-menu
                value="support1"   #Don't change this value otherwise the code will not work anymore!!!!
            ),
            disnake.SelectOption(
                label="Have a question",  #Name of the 2 Select Menu Option
                description="If you have any question to ask qo here", #Description of the 2 Select Menu Option
                emoji="🤔",        #Emoji of the 2 Option  if you want a Custom Emoji read this  https://github.com/Simoneeeeeeee/Discord-Select-Menu-Ticket-Bot/tree/main#how-to-use-custom-emojis-from-your-discors-server-in-the-select-menu
                value="support2"   #Don't change this value otherwise the code will not work anymore!!!!
            )
        ]
    )
    async def callback(self, select, interaction):
        if "support1" in interaction.data['values']: 
            if interaction.channel.id == TICKET_CHANNEL:
                guild = self.bot.get_guild(GUILD_ID)
                member_id = interaction.user.id
                member_name = interaction.user.name
                cur.execute("SELECT discord_id FROM ticket WHERE discord_id=?", (member_id,)) #Check if the User already has a Ticket open
                existing_ticket = cur.fetchone()
                if existing_ticket is None:
                    cur.execute("INSERT INTO ticket (discord_name, discord_id) VALUES (?, ?)", (member_name, member_id)) #If the User doesn't have a Ticket open it will insert the User into the Database and create a Ticket
                    conn.commit()
                    cur.execute("SELECT id FROM ticket WHERE discord_id=?", (member_id,)) #Get the Ticket Number from the Database
                    ticket_number = cur.fetchone()
                    category = self.bot.get_channel(CATEGORY_ID1)
                    ticket_channel = await guild.create_text_channel(f"ticket-{ticket_number}", category=category,
                                                                    topic=f"{interaction.user.id}")

                    await ticket_channel.set_permissions(guild.get_role(TEAM_ROLE1), send_messages=True, read_messages=True, add_reactions=False, #Set the Permissions for the Staff Team
                                                        embed_links=True, attach_files=True, read_message_history=True,
                                                        external_emojis=True)
                    await ticket_channel.set_permissions(interaction.user, send_messages=True, read_messages=True, add_reactions=False, #Set the Permissions for the User
                                                        embed_links=True, attach_files=True, read_message_history=True,
                                                        external_emojis=True)
                    await ticket_channel.set_permissions(guild.default_role, send_messages=False, read_messages=False, view_channel=False) #Set the Permissions for the @everyone role
                    embed = disnake.Embed(description=f'Welcome {interaction.user.mention},\n'
                                                       'describe your Problem and our Support will help you soon.',   #Ticket Welcome message
                                                    color=disnake.colour.Color.blue())
                    await ticket_channel.send(embed=embed, view=CloseButton(bot=self.bot))

                    embed = disnake.Embed(description=f'📬 Ticket was Created! Look here --> {ticket_channel.mention}',  
                                            color=disnake.colour.Color.green())
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    await asyncio.sleep(1)
                    embed = disnake.Embed(title="🎫 Need help ? 🎫", description="If you have a problem, a question, a proposal or anything else, come and tell us about it in a ticket.", color=disnake.colour.Color.blue())  
                    await interaction.message.edit(embed=embed, view=MyView(bot=self.bot)) #This will reset the SelectMenu in the Ticket Channel
                else:
                    embed = disnake.Embed(title=f"You already have a open Ticket", color=0xff0000)
                    await interaction.response.send_message(embed=embed, ephemeral=True) #This will tell the User that he already has a Ticket open
                    await asyncio.sleep(1)
                    embed = disnake.Embed(title="🎫 Need help ? 🎫", description="If you have a problem, a question, a proposal or anything else, come and tell us about it in a ticket.", color=disnake.colour.Color.blue())
                    await interaction.message.edit(embed=embed, view=MyView(bot=self.bot)) #This will reset the SelectMenu in the Ticket Channel
        if "support2" in interaction.data['values']:
            if interaction.channel.id == TICKET_CHANNEL:
                guild = self.bot.get_guild(GUILD_ID)
                member_id = interaction.user.id
                member_name = interaction.user.name
                cur.execute("SELECT discord_id FROM ticket WHERE discord_id=?", (member_id,)) #Check if the User already has a Ticket open
                existing_ticket = cur.fetchone()
                if existing_ticket is None:
                    cur.execute("INSERT INTO ticket (discord_name, discord_id) VALUES (?, ?)", (member_name, member_id)) #If the User doesn't have a Ticket open it will insert the User into the Database and create a Ticket
                    conn.commit()
                    cur.execute("SELECT id FROM ticket WHERE discord_id=?", (member_id,)) #Get the Ticket Number from the Database
                    ticket_number = cur.fetchone()
                    category = self.bot.get_channel(CATEGORY_ID2)
                    ticket_channel = await guild.create_text_channel(f"ticket-{ticket_number}", category=category,
                                                                    topic=f"{interaction.user.id}")

                    await ticket_channel.set_permissions(guild.get_role(TEAM_ROLE2), send_messages=True, read_messages=True, add_reactions=False, #Set the Permissions for the Staff Team
                                                        embed_links=True, attach_files=True, read_message_history=True,
                                                        external_emojis=True)
                    await ticket_channel.set_permissions(interaction.user, send_messages=True, read_messages=True, add_reactions=False, #Set the Permissions for the User
                                                        embed_links=True, attach_files=True, read_message_history=True,
                                                        external_emojis=True)
                    await ticket_channel.set_permissions(guild.default_role, send_messages=False, read_messages=False, view_channel=False) #Set the Permissions for the @everyone role
                    embed = disnake.Embed(description=f'Welcome {interaction.user.mention},\n' #Ticket Welcome message
                                                       'how can i help you?',
                                                    color=disnake.colour.Color.blue())
                    await ticket_channel.send(embed=embed, view=CloseButton(bot=self.bot))

                    embed = disnake.Embed(description=f'📬 Ticket was Created! Look here --> {ticket_channel.mention}',
                                            color=disnake.colour.Color.green())
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    await asyncio.sleep(1)
                    embed = disnake.Embed(title="🎫 Need help ? 🎫", description="If you have a problem, a question, a proposal or anything else, come and tell us about it in a ticket.", color=disnake.colour.Color.blue())
                    await interaction.message.edit(embed=embed, view=MyView(bot=self.bot)) #This will reset the SelectMenu in the Ticket Channel
                else:
                    embed = disnake.Embed(title=f"You already have a open Ticket", color=0xff0000)
                    await interaction.response.send_message(embed=embed, ephemeral=True) #This will tell the User that he already has a Ticket open
                    await asyncio.sleep(1)
                    embed = disnake.Embed(title="🎫 Need help ? 🎫", description="If you have a problem, a question, a proposal or anything else, come and tell us about it in a ticket.", color=disnake.colour.Color.blue())
                    await interaction.message.edit(embed=embed, view=MyView(bot=self.bot)) #This will reset the SelectMenu in the Ticket Channel
        return

#First Button for the Ticket 
class CloseButton(disnake.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @disnake.ui.button(label="Close Ticket 🎫", style = disnake.ButtonStyle.blurple, custom_id="close")
    async def close(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        guild = self.bot.get_guild(GUILD_ID)
        ticket_creator = int(interaction.channel.topic)
        cur.execute("SELECT id FROM ticket WHERE discord_id=?", (ticket_creator,))  # Get the Ticket Number from the Database
        ticket_number = cur.fetchone()
        ticket_creator = guild.get_member(ticket_creator)

        embed = disnake.Embed(title="Ticket Closed 🎫", description="Press Reopen to open the Ticket again or Delete to delete the Ticket!", color=disnake.colour.Color.green())
        await interaction.channel.set_permissions(ticket_creator, send_messages=False, read_messages=False, add_reactions=False,
                                                        embed_links=False, attach_files=False, read_message_history=False, #Set the Permissions for the User if the Ticket is closed
                                                        external_emojis=False)
        await interaction.channel.edit(name=f"ticket-closed-{ticket_number}")
        await interaction.response.send_message(embed=embed, view=TicketOptions(bot=self.bot)) #This will show the User the TicketOptions View
        button.disabled = True
        await interaction.message.edit(view=self)

#Converts the Time to a Timestamp
def convert_time_to_timestamp(timestamp):
    timestamp_str = timestamp[0]

    datetime_obj = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    discord_timestamp = int(datetime_obj.timestamp())
    return discord_timestamp


#Buttons to reopen or delete the Ticket
class TicketOptions(disnake.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    @disnake.ui.button(label="Reopen Ticket 🎫", style = disnake.ButtonStyle.green, custom_id="reopen")
    async def reopen_button(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        guild = self.bot.get_guild(GUILD_ID)
        ticket_creator = int(interaction.channel.topic)
        cur.execute("SELECT id FROM ticket WHERE discord_id=?", (ticket_creator,)) #Get the Ticket Number from the Database
        ticket_number = cur.fetchone()        
        embed = disnake.Embed(title="Ticket Reopened 🎫", description="Press Delete Ticket to delete the Ticket!", color=disnake.colour.Color.green()) #The Embed for the Ticket Channel when it got reopened
        ticket_creator = guild.get_member(ticket_creator)
        await interaction.channel.set_permissions(ticket_creator, send_messages=True, read_messages=True, add_reactions=False,
                                                        embed_links=True, attach_files=True, read_message_history=True, #Set the Permissions for the User if the Ticket is reopened
                                                        external_emojis=False)
        await interaction.channel.edit(name=f"ticket-{ticket_number}") #Edit the Ticket Channel Name again
        await interaction.response.send_message(embed=embed)

    @disnake.ui.button(label="Delete Ticket 🎫", style = disnake.ButtonStyle.red, custom_id="delete")
    async def delete_button(self, button: disnake.ui.Button, interaction: disnake.Interaction):
        guild = self.bot.get_guild(GUILD_ID)
        channel = self.bot.get_channel(LOG_CHANNEL)
        ticket_creator = int(interaction.channel.topic)

        cur.execute("SELECT ticket_created FROM ticket WHERE discord_id=?", (ticket_creator,)) #Get the Ticket Created Time from the Database
        ticket_created = cur.fetchone()
        discord_timestamp = convert_time_to_timestamp(ticket_created) #Convert the Time to a Timestamp

        cur.execute("DELETE FROM ticket WHERE discord_id=?", (ticket_creator,)) #Delete the Ticket from the Database
        conn.commit()

        #Creating the Transcript
        military_time: bool = True
        transcript = await chat_exporter.export(
            interaction.channel,
            limit=200,
            tz_info=TIMEZONE,
            military_time=military_time,
            bot=self.bot,
        )       
        if transcript is None:
            return
        
        transcript_file = disnake.File(
            io.BytesIO(transcript.encode()),
            filename=f"transcript-{interaction.channel.name}.html")
        transcript_file2 = disnake.File(
            io.BytesIO(transcript.encode()),
            filename=f"transcript-{interaction.channel.name}.html")
        
        ticket_creator = guild.get_member(ticket_creator)
        embed = disnake.Embed(description=f'Ticket is deliting in 5 seconds.', color=0xff0000)
        transcript_info = disnake.Embed(title=f"Ticket Deleting | {interaction.channel.name}", description=f"Ticket from: {ticket_creator.mention}\nTicket Name: {interaction.channel.name}\n Ticket Created at: <t:{discord_timestamp}:F> \n Closed from: {interaction.user.mention}", color=disnake.colour.Color.blue())

        await interaction.response.send_message(embed=embed)
        #checks if user has dms disabled
        try:
            await ticket_creator.send(embed=transcript_info, file=transcript_file)
        except:
            transcript_info.add_field(name="Error", value="Couldn't send the Transcript to the User because he has his DMs disabled!", inline=True)
        await channel.send(embed=transcript_info, file=transcript_file2)
        await asyncio.sleep(3)
        await interaction.channel.delete(reason="Ticket got Deleted!")
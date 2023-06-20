import disnake
import json
from disnake.ext import commands

class InviteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invite_data = {}
        self.load_invite_data()

    def load_invite_data(self):
        try:
            with open('data/invite.json', 'r') as file:
                self.invite_data = json.load(file)
        except FileNotFoundError:
            self.invite_data = {}

    def save_invite_data(self):
        with open('data/invite.json', 'w') as file:
            json.dump(self.invite_data, file, indent=4)

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        inviter_id = str(invite.inviter.id)

        if inviter_id not in self.invite_data:
            self.invite_data[inviter_id] = 1
        else:
            self.invite_data[inviter_id] += 1

        self.save_invite_data()

    @commands.slash_command(name="invites", description="Displays the number of invites for a member")
    async def invites(self, ctx, member: disnake.Member):
        member_id = str(member.id)
        if member_id in self.invite_data:
            invite_count = self.invite_data[member_id]
            await ctx.send(f"{member.display_name} has invited {invite_count} person(s).")
        else:
            await ctx.send(f"{member.display_name} has no invitations.")

    @commands.slash_command(name="clear-invites", description="Clears the invites of a member")
    async def clear_invites(self, ctx, member: disnake.Member):
        member_id = str(member.id)
        if member_id in self.invite_data:
            del self.invite_data[member_id]
            self.save_invite_data()
            await ctx.send(f"The invitations of {member.display_name} have been cleared.")
        else:
            await ctx.send(f"{member.display_name} has no invitations to clear.")

    @commands.slash_command(name="top-invite", description="Displays the top 10 members with the most invitations")
    async def top_invite(self, ctx):
        sorted_invites = sorted(self.invite_data.items(), key=lambda x: x[1], reverse=True)
        top_10 = sorted_invites[:10]

        embed = disnake.Embed(title="Top 10 Members with the Most Invitations")
        for idx, (member_id, invite_count) in enumerate(top_10, start=1):
            member = self.bot.get_user(int(member_id))
            if member:
                embed.add_field(name=f"{idx}. {member.display_name}", value=f"Invitations: {invite_count}", inline=False)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(InviteCog(bot))

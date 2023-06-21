import disnake
from disnake.ext import commands
import json

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warns_file = 'data/warns.json'
        self.load_warns()

    def load_warns(self):
        try:
            with open(self.warns_file, 'r') as file:
                self.warns = json.load(file)
        except FileNotFoundError:
            self.warns = {}

    def save_warns(self):
        with open(self.warns_file, 'w') as file:
            json.dump(self.warns, file, indent=4)

    @commands.slash_command(name="kick", description="Kick a member from the server.")
    @commands.has_permissions(kick_members=True)
    async def slash_kick(self, ctx, member: disnake.Member, reason: str = None):
        """Kick a member from the server."""
        await member.kick(reason=reason)
        await ctx.send(f"{member.mention} has been kicked.")

    @commands.slash_command(name="ban", description="Ban a member from the server.")
    @commands.has_permissions(ban_members=True)
    async def slash_ban(self, ctx, member: disnake.Member, reason: str = None):
        """Ban a member from the server."""
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} has been banned.")

    @commands.slash_command(name="mute", description="Mute a member in the server.")
    @commands.has_permissions(manage_roles=True)
    async def slash_mute(self, ctx, member: disnake.Member, *, reason: str = None):
        """Mute a member in the server."""
        mute_role = disnake.utils.get(ctx.guild.roles, name="Muted")  # Replace "Muted" with the name of your mute role
        if mute_role:
            await member.add_roles(mute_role, reason=reason)
            await ctx.send(f"{member.mention} has been muted. Reason: {reason}" if reason else f"{member.mention} has been muted.")
        else:
            await ctx.send("Mute role not found. Please create a role named 'Muted'.")

    @commands.slash_command(name="unmute", description="Unmute a member in the server.")
    @commands.has_permissions(manage_roles=True)
    async def slash_unmute(self, ctx, member: disnake.Member):
        """Unmute a member in the server."""
        mute_role = disnake.utils.get(ctx.guild.roles, name="Muted")  # Replace "Muted" with the name of your mute role
        if mute_role:
            await member.remove_roles(mute_role)
            await ctx.send(f"{member.mention} has been unmuted.")
        else:
            await ctx.send("Mute role not found. Please create a role named 'Muted'.")

    @commands.slash_command(name="unban", description="Unban a member from the server.")
    @commands.has_permissions(ban_members=True)
    async def slash_unban(self, ctx, member: disnake.User):
        """Unban a member from the server."""
        bans = await ctx.guild.bans()
        for ban_entry in bans:
            if ban_entry.user.id == member.id:
                await ctx.guild.unban(member)
                await ctx.send(f"{member.mention} has been unbanned.")
                return
        await ctx.send(f"{member.mention} is not banned.")

    @commands.slash_command(name="warn", description="Warn a member.")
    @commands.has_permissions(kick_members=True)
    async def slash_warn(self, ctx, member: disnake.Member, *, reason: str):
        """Warn a member."""
        if str(member.id) not in self.warns:
            self.warns[str(member.id)] = []

        self.warns[str(member.id)].append(reason)
        self.save_warns()

        await ctx.send(f"{member.mention} has been warned for: {reason}")

    @commands.slash_command(name="warns", description="Get the warnings for a member.")
    @commands.has_permissions(kick_members=True)
    async def slash_warns(self, ctx, member: disnake.Member):
        """Get the warnings for a member."""
        if str(member.id) in self.warns:
            warnings = self.warns[str(member.id)]
            embed = disnake.Embed(title=f"Warnings for {member.display_name}", description="\n".join(warnings), color=disnake.Color.orange())
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{member.mention} has no warnings.")

    @commands.slash_command(name="clear", description="Clear a specified number of messages.")
    @commands.has_permissions(manage_messages=True)
    async def slash_clear(self, ctx, amount: int):
        """Clear a specified number of messages."""
        await ctx.channel.purge(limit=amount + 1)

        embed = disnake.Embed(
            title="Message Clear",
            description=f"Cleared {amount} messages.",
            color=disnake.Color.green()
        )
        await ctx.send(embed=embed, delete_after=5)


    @commands.Cog.listener()
    async def on_ready(self):
        print('Moderation cog is ready!')

def setup(bot):
    bot.add_cog(ModerationCog(bot))

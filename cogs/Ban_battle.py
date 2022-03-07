import discord
from discord.ext import commands
from discord.ext.commands import bot
from utils.checks import checks

class Invite_Panel(discord.ui.View):
    def __init__(self, staff_invite, public_invite):
        super().__init__(timeout=3600)
        self.staff_invite = staff_invite
        self.public_invite = public_invite

    @discord.ui.button(label="Staff-invite", style=discord.ButtonStyle.red, custom_id="staff-invite")
    async def staff_invite(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user.guild_permissions.administrator or interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message(self.staff_invite,ephemeral=True)
        else:
            await interaction.response.send_message("You don't have permission to use this button.", ephemeral=True)
    
    @discord.ui.button(label="Public Invite", style=discord.ButtonStyle.green, custom_id="public-invite")
    async def public_invite(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message(self.public_invite, ephemeral=True)

class Cog_name(commands.Cog, description="Ban Battle Event Module"): 
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__} Cog has been loaded\n-----')
    
    @commands.group(invoke_without_command=True)
    @commands.check_any(checks.can_use())
    async def Ban(self, ctx):
        await ctx.send("add Subcommand")
    
    @Ban.group(name="setup", description="Setup Ban battle server")
    @commands.check_any(checks.can_use())
    async def setup(self, ctx):
        
        guild = await self.bot.create_guild(name="Ban Battle", code="acTyYdtYyz3d")
        overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False, view_channel=False)}
        update = {guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False)}

        staff_channel = await guild.create_text_channel(name="Staff-Channel", overwrites=overwrites)
        public_channel = await guild.create_text_channel(name="Ban-everyone", overwrites=update)
        Staff_invite = await staff_channel.create_invite(max_uses=0, max_age=0)
        public_invite = await public_channel.create_invite(max_uses=100, max_age=0)
        
        embed = discord.Embed(title="Ban Battle", description=f"ban battle server has been created by {ctx.author.mention}\nThere are two invite links ones", color=0x0af4f1)
        embed.add_field(name="Staff-invite", value="Total Usage: unlimited", inline=False)
        embed.add_field(name="Public-invite", value="Total Usage: 100", inline=False)
        embed.set_footer(text="Ban Battle", icon_url=ctx.guild.icon.url)
        message  = await ctx.send(embed=embed, view=Invite_Panel(Staff_invite, public_invite))
        broadcast = await message.create_thread(name="Bans Broadcast",auto_archive_duration=60)
        data = { "_id": guild.id,'guildID': guild.id, 'staff_channel': staff_channel.id, 'public_channel': public_channel.id, 'broadcast': broadcast.id}
        await self.bot.ban_backup.upsert(data)
        self.bot.ban_event[guild.id] = data

    @Ban.group(name="Takeover", description="Takeover Ban battle server")
    @commands.check_any(checks.can_use())
    async def takeover(self, ctx, guild: discord.Guild):
        if guild.owner_id == self.bot.user.id:
            await guild.edit(owner=ctx.author)
            await ctx.send(f"{guild.name} has been taken over by {ctx.author.name}")
            return

    @Ban.group(name="cleanup", description="Cleanup Ban battle server")
    @commands.check_any(checks.can_use())
    async def cleanup(self, ctx):
        for guild in self.bot.guilds:
            try:
                name = guild.name

                await guild.delete()
                await self.bot_event.delete(guild.id)
            except:
                pass
        await ctx.message.add_reaction("✅")

    @Ban.group(name="start", description="Start Ban battle server")
    @commands.check_any(checks.can_use())
    async def start(self, ctx):
        if ctx.guild.name == "Ban Battle":
            for invites in await ctx.guild.invites():
                await invites.delete()
            channel = ctx.guild.get_channel(self.bot.ban_event[ctx.guild.id]['public_channel'])
            print(channel)
            overwrite = channel.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = True

            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            await ctx.message.add_reaction("✅")
            await ctx.send("Ban battle server has been started")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        main_guild = self.bot.get_guild(785839283847954433)
        if member.guild.name == "Ban Battle":
            if member not in main_guild.members:                
                try:
                    await member.send("Your not in Main Server Pls join it")
                except discord.HTTPException:
                    pass
                await member.kick(reason="No in Main Server")

            role = discord.utils.get(member.guild.roles, name="TG Staff")
            if member.id in [488614633670967307, 301657045248114690,413651113485533194,651711446081601545]:
                await member.add_roles(role)

    @commands.command(name="Eliminat", description="eliminate a user from ban battle", aliases=["el"])
    async def ban(self, ctx, member: discord.Member):
        if ctx.guild.name == "Ban Battle":
            role = discord.utils.get(ctx.guild.roles, name="TG Staff")
            if role in member.roles:
                return await ctx.send("You can't eliminat this user")
            #await member.ban(delete_message_days=0, reason="Eliminated")
            broadcast = self.bot.get_channel(self.bot.ban_event[member.guild.id]['broadcast'])
            await broadcast.send(f"{ctx.author.mention} has eliminated {member.mention}")
            await ctx.send(f"{member.name} has been banned")

def setup(bot):
    bot.add_cog(Cog_name(bot))
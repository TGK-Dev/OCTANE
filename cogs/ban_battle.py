from discord import app_commands, Interaction
from discord.ext import commands
from ui.buttons import Invite_Panel
from utils.checks import Commands_Checks
import asyncio
import discord

class Ban_battle_Slash(app_commands.Group, name="bb", description="ban Battle Module"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(name='bb')
    
    @app_commands.command(name="create", description="Create a new ban battle")
    @app_commands.guilds(785839283847954433)
    async def create(self, interaction: Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        
        guild = await self.bot.create_guild(name="Ban Battle", code="acTyYdtYyz3d")
        overwrites = {guild.default_role: discord.PermissionOverwrite(read_messages=False, view_channel=False)}
        update = {guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False)}

        staff_channel = await guild.create_text_channel(name="Staff-Channel", overwrites=overwrites)
        public_channel = await guild.create_text_channel(name="Ban-everyone", overwrites=update)
        Staff_invite = await staff_channel.create_invite(max_uses=0, max_age=0)
        public_invite = await public_channel.create_invite(max_uses=100, max_age=0)
        
        embed = discord.Embed(title="Ban Battle", description=f"ban battle server has been created by {interaction.user.mention}\nThere are two invite links ones", color=0x0af4f1)
        embed.add_field(name="Staff-invite", value="Total Usage: unlimited", inline=False)
        embed.add_field(name="Public-invite", value="Total Usage: 100", inline=False)
        embed.set_footer(text="Ban Battle", icon_url=interaction.guild.icon.url)
        message  = await interaction.channel.send(embed=embed, view=Invite_Panel(Staff_invite, public_invite))
        broadcast = await message.create_thread(name="Bans Broadcast",auto_archive_duration=60)
        data = { "_id": guild.id,'guildID': guild.id, 'staff_channel': staff_channel.id, 'public_channel': public_channel.id, 'broadcast': broadcast.id}
        await self.bot.ban_backup.insert(data)
        self.bot.ban_event[guild.id] = data
        await interaction.followup.send(f"{interaction.user.mention} created a new ban battle server", ephemeral=True)

        embed = discord.Embed(title="Event", description="Ban Battle", color=0x0af4f1)
        description = "》Every player will have perms to use the `ban` command\n》When the game starts, the event channel will be unlocked and players can Ban other players using `-eliminate @user`\n》Last player standing wins!"
        embed.add_field(name="**How to play**", value=description, inline=False)
        embed.add_field(name="Note", value="Members with the role `@TGK Event Staff` cannot be banned. They'll be present to moderate, not participate.", inline=False)

        ping_msg = await public_channel.send(embed=embed)
        await ping_msg.pin()

    @app_commands.command(name="clean", description="Clean the ban battle servers")
    @app_commands.guilds(785839283847954433)
    async def clean(self, interaction: Interaction, guild: int):
        await interaction.response.send_message("Cleaning Ban Battle Servers", ephemeral=True)
        guild = await self.bot.get_guild(guild)
        if guild:
            if guild.owner.id == self.bot.user.id:
                await guild.delete()
                await interaction.response.send_message("Ban Battle Servers hav been cleaned", ephemeral=True)
                await self.bot.ban_backup.delete(guild.id)
        
        else:
            await interaction.response.send_message("Enter a valid guild id", ephemeral=True)


class Ban_Battle(commands.Cog, name="Ban Battle", description="Ban Battle Module"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(self.bot.user.name)
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
        self.bot.tree.add_command(Ban_battle_Slash(self.bot), guild=discord.Object(785839283847954433))
        self.bot.tree.add_command(Ban_battle_Slash(self.bot), guild=discord.Object(811037093715116072))

    @commands.group(invoke_without_command=True)
    @commands.check_any(Commands_Checks.can_use())
    async def bb(self, ctx):
        await ctx.send("add Subcommand")
    
    @bb.group(name="start", description="Start Ban battle server")
    #@commands.check_any(Commands_Checks.can_use())
    async def start(self, ctx):
        if ctx.guild.name == "Ban Battle" and ctx.author.guild_permissions.administrator:
            for invites in await ctx.guild.invites():
                await invites.delete()

            channel = ctx.guild.get_channel(self.bot.ban_event[ctx.guild.id]['public_channel'])
            overwrite = channel.overwrites_for(ctx.guild.default_role)
            overwrite.send_messages = True

            embed = discord.Embed(description=f"Ban battle game has started by {ctx.author.mention}\n You can start banning people with command `-eliminame`\nYou can't ban user who has `@TGK Event Staff` Role", color=0x0af4f1)
            await channel.send(content="@everyone Game Starting in 5s", embed=embed)
            await asyncio.sleep(3)
            await channel.send("unlocking the channel")
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            await channel.send("Game has started")
            await ctx.message.add_reaction("✅")
    
    @commands.command(name="eliminate", description="Eliminate a user from ban battle", aliases=["el"])
    @commands.check_any(Commands_Checks.is_ban_server())
    async def Eliminate(self, ctx, member: discord.Member):
        if ctx.guild.name == "Ban Battle" and ctx.author.guild_permissions.administrator:

            role = discord.utils.get(ctx.guild.roles, name="TGK Event Staff")

            if role in member.roles:
                return await ctx.send("You can't eliminat this user")
            if member == self.bot.user:
                return await ctx.send("You can't eliminat me")

            await member.ban(delete_message_days=0, reason="Eliminated")
            broadcast = self.bot.get_channel(self.bot.ban_event[member.guild.id]['broadcast'])
            await broadcast.send(f"{ctx.author.mention} has eliminated {member.mention}")
            await ctx.send(f"{member.name} has been banned")
    
    @bb.group(name="winner", description="Make someone the winner of the game")
    @commands.check_any(Commands_Checks.is_ban_server())
    async def winner(self, ctx, member: discord.Member):
        if ctx.guild.name == "Ban Battle":
           broadcast = self.bot.get_channel(self.bot.ban_event[member.guild.id]['broadcast'])
           embed = discord.Embed(description=f"🏆 | {member.mention} has won the game", color=0x0af4f1)
           await broadcast.send(f"{member.mention}",embed=embed)
           await broadcast.edit(name=f"🏆 | {member.name} has won the game")
           await asyncio.sleep(10)
           await broadcast.edit(archived=True, locked=True)
           await ctx.message.add_reaction("✅")
    
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

            role = discord.utils.get(member.guild.roles, name="TGK Event Staff")
            public = discord.utils.get(member.guild.roles, name="Alive")
            if member.id in [488614633670967307, 301657045248114690, 651711446081601545, 562738920031256576, 413651113485533194, 457839031909351425, 680183321829179444, 766792610059780118]:
                await member.add_roles(role)
            else:
                await member.add_roles(public)

async def setup(bot):
    await bot.add_cog(Ban_Battle(bot))




#make an info embed about how to play ban battle



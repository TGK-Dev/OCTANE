from discord import app_commands
from discord.ext import commands
from ui.Ticket_system import Ticket_main, Ticket_Control
from discord.app_commands import Choice
from discord import Interaction
from typing import Union
from utils.checks import Commands_Checks
from utils.functions import make_db_temp
import discord

class Ticket_slash(app_commands.Group, name="ticket", description="ticket system commands"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(name='ticket')

    @app_commands.command(name="config", description="configure ticket system")
    @app_commands.describe(option="configure settings option", target="your option")
    @app_commands.choices(option=[Choice(name="Support Channel", value="support_channel"), Choice(name="Category", value="ticket_category"), Choice(name="Log Channel", value="ticket_log"), Choice(name="Transcript", value="transcript")])
    @app_commands.guilds(785839283847954433)
    async def config(self, interaction: Interaction, option: Choice[str], target: Union[discord.TextChannel, discord.CategoryChannel]):
        await interaction.response.defer()
        guild_data = await self.bot.config.find(interaction.guild.id)
        if guild_data is None:
            guild_data = make_db_temp(interaction.guild.id)
            await self.bot.config.insert(guild_data)
        ticket_data = guild_data['Tickets']
        Change = ""
        if option.value == "support_channel":
            ticket_data['channel'] = target.id
            Change += f"Support channel set to {target.mention}"
        
        elif option.value == "ticket_category":
            ticket_data['category'] = target.id
            Change += f"Ticket category set to `{target.name}`"
        
        elif option.value == "ticket_log":
            ticket_data['log_channel'] = target.id
            Change += f"Ticket log channel set to {target.mention}"
        
        elif option.value == "transcript":
            ticket_data['transcript'] = target.id
            Change += f"Transcript channel set to {target.mention}"
        
        await self.bot.config.update(guild_data)
        await interaction.followup.send(Change)

    @app_commands.command(name="add", description="add user/role to ticket")
    @app_commands.guilds(785839283847954433)
    @app_commands.describe(option="Select Option")
    @app_commands.describe(target="User/Role")
    async def edit(self, interaction: Interaction, target: Union[discord.Member, discord.Role]):
        await interaction.response.send_message(f"Adding Taraget to Ticket")
        data = await self.bot.ticket.find(interaction.channel.id)
        if data is None:
            await interaction.edit_original_message(content="Invalid Ticket")
            return

        if target.id in data['added_users'] or target.id in data['added_roles']:
            await interaction.edit_original_message(content="Target already in Ticket")
            return
        else:
            if isinstance(target, discord.Member):
                data['added_users'].append(target.id)
            elif isinstance(target, discord.Role):
                data['added_roles'].append(target.id)
            await self.bot.ticket.update(data)
            await interaction.channel.set_permissions(target, permissions=discord.PermissionOverwrite(read_messages=True, send_messages=True, add_reactions=True, attach_files=True, embed_links=True))
            embed = discord.Embed(description=f"{target.mention} has been added to the ticket", color=0x00ff00)
            await interaction.edit_original_message(content=None, embed=embed)
    
    @app_commands.command(name="remove", description="remove user/role from ticket")
    @app_commands.guilds(785839283847954433)
    @app_commands.describe(option="Select Option")
    @app_commands.describe(target="User/Role")
    async def remove(self, interaction: Interaction, target: Union[discord.Member, discord.Role]):
        await interaction.response.send_message(f"Removing Taraget from Ticket")
        data = await self.bot.ticket.find(interaction.channel.id)
        if data is None:
            await interaction.edit_original_message(content="Invalid Ticket")
            return

        if target.id not in data['added_users'] and target.id not in data['added_roles']:
            await interaction.edit_original_message(content="Target not in Ticket")
            return
        else:
            if isinstance(target, discord.Member):
                data['added_users'].remove(target.id)
            elif isinstance(target, discord.Role):
                data['added_roles'].remove(target.id)
            await self.bot.ticket.update(data)
            await interaction.channel.set_permissions(target, permissions=discord.PermissionOverwrite(read_messages=False, send_messages=False, add_reactions=False, attach_files=False, embed_links=False))
            embed = discord.Embed(description=f"{target.mention} has been removed from the ticket", color=0x00ff00)
            await interaction.edit_original_message(content=None, embed=embed)

class Ticket(commands.Cog, name="Ticket System", description="Create Ticket Without Any Worry"):
    def __init__(self, bot,):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(Ticket_main(self.bot))
        self.bot.add_view(Ticket_Control(self.bot))
        self.bot.tree.add_command(Ticket_slash(self.bot), guild=discord.Object(785839283847954433))
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @commands.command()
    async def setup(self, ctx):
        embed = discord.Embed(title="Support Centre",description="This channel is for in-server support purpose only, talking anything here which is not related to the channel usage will result in warn or mute, mini-modding is also not allowed, we have enough staff members to handle it. Thank you for your cooperation.",color=0xff0000)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
        await ctx.send(embed=embed, view=Ticket_main(self.bot))

async def setup(bot):
    await bot.add_cog(Ticket(bot))
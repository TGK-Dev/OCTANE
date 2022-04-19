from discord import app_commands
from discord.ext import commands
from ui.Ticket_system import Ticket_main, Ticket_Control
from discord.app_commands import Choice
from discord import Interaction
from typing import Union
import discord

class Ticket_slash(app_commands.Group, name="ticket", description="ticket system commands"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(name='ticket')
    
    @app_commands.command(name="edit", description="Edit Ticket")
    @app_commands.guilds(964377652813234206)
    @app_commands.describe(option="Select Option")
    @app_commands.describe(target="User/Role")
    @app_commands.choices(option=[
        Choice(name="Add", value=1),
        Choice(name="Remove", value=2),
        Choice(name="Panel", value=3)
    ])
    async def edit(self, interaction: Interaction, option: Choice[int], target: Union[discord.Member, discord.Role]=None):

        if option.value == 1:
            await  interaction.response.defer(thinking=True)

            ticket_data = await self.bot.ticket.find(interaction.channel.id)
            if ticket_data is None: return await interaction.followup.send("Ticket Not Found")

            if target.id in ticket_data['added_roles'] or ticket_data['added_users']:
                return await interaction.followup.send(f"{target.mention} Already Added", allowed_mentions=discord.AllowedMentions(users=False, roles=False))

            if type(target) == discord.Role:
                ticket_data['added_roles'].append(target.id)
            elif type(target) == discord.Member:
                ticket_data['added_users'].append(target.id)
            
            overwrite = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_messages=True, attach_files=True)
            await interaction.channel.set_permissions(target, overwrite=overwrite)
            await self.bot.ticket.update(ticket_data)

            await interaction.followup.send(embed=discord.Embed(description=f"<:allow:819194696874197004> | {target.mention} added to the ticket", color=0x2f3136))
        
        elif option.value == 2:
            await  interaction.response.defer(thinking=True)

            ticket_data = await self.bot.ticket.find(interaction.channel.id)
            if ticket_data is None: return await interaction.followup.send("Ticket Not Found")

            if target.id not in ticket_data['added_roles'] and target.id not in ticket_data['added_users']:
                return await interaction.followup.send(f"{target.mention} Not Added", allowed_mentions=discord.AllowedMentions(users=False, roles=False))

            if type(target) == discord.Role:
                ticket_data['added_roles'].remove(target.id)
            elif type(target) == discord.Member:
                ticket_data['added_users'].remove(target.id)
            
            overwrite = discord.PermissionOverwrite(view_channel=False, send_messages=False, read_messages=False, attach_files=False)
            await interaction.channel.set_permissions(target, overwrite=overwrite)
            await self.bot.ticket.update(ticket_data)

            await interaction.followup.send(embed=discord.Embed(description=f"<:allow:819194696874197004> | {target.mention} removed from the ticket", color=0x2f3136))
        
        elif option.value == 3:

            await interaction.response.defer(thinking=True)
            Panel_embed = discord.Embed(title="Ticket Control Panel",color=0x008000)
            ticket_data = await self.bot.ticket.find(interaction.channel.id)
            Panel_embed.description = f"""**Open**: To Open current Ticket\n**Close**: To Close current Ticket\n**Secure**: Make Ticket Adminitrator Only\n**Save**: Save Ticket Transhcript\n**Delete**: Delete Ticket\n**Add Shero**: add Shero bot to Ticket only works in Partnership Ticket\n"""
            View = Ticket_Control(self.bot)
            
            if ticket_data['type'] == "partnership":
                await interaction.followup.send(embed=Panel_embed, view=View)

            elif ticket_data['type'] == "support":
                for button in View.children:
                    if button.label == "Add Shero":
                        item = button
                        break
                View.remove_item(item)
                await interaction.followup.send(embed=Panel_embed, view=View)

class Ticket(commands.Cog, name="Ticket System", description="Create Ticket Without Any Worry"):
    def __init__(self, bot,):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(Ticket_main(self.bot))
        self.bot.add_view(Ticket_Control(self.bot))
        self.bot.tree.add_command(Ticket_slash(self.bot), guild=discord.Object(964377652813234206))
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @commands.command()
    async def setup(self, ctx):
        embed = discord.Embed(title="Support Centre",description="This channel is for in-server support purpose only, talking anything here which is not related to the channel usage will result in warn or mute, mini-modding is also not allowed, we have enough staff members to handle it. Thank you for your cooperation.",color=0xff0000)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
        await ctx.send(embed=embed, view=Ticket_main(self.bot))

async def setup(bot):
    await bot.add_cog(Ticket(bot))
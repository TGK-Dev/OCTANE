import asyncio
import chat_exporter
import discord
import io
from discord.ext import commands
from typing import Union
from utils.checks import checks
from Views.Ticket_panel import *

description = "Ticket System For the Server Support"

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(Ticket_panel(self.bot))
        print(f'{self.__class__.__name__} Cog has been loaded\n-----')

    @commands.command()
    @commands.check_any(checks.is_me(), checks.can_use())
    async def setup(self, ctx):
        embed = discord.Embed(title="Support Centre",description="This channel is for in-server support purpose only, talking anything here which is not related to the channel usage will result in warn or mute, mini-modding is also not allowed, we have enough staff members to handle it. Thank you for your cooperation.",color=0xff0000)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
        await ctx.send(embed=embed, view=Ticket_panel(self.bot))

    @commands.command(name="close", description="Close Current Ticket")
    @commands.check_any(checks.can_use())
    async def close(self, ctx):
        await ctx.send("This commands has moved to Slash Command", delete_after=10)
        # data = await self.bot.ticket.find_by_custom({'channel': ctx.channel.id, 'guild': ctx.guild.id})
        # if not data: return await ctx.send("Please use this command only in tickets")
        # user = ctx.guild.get_member(int(data['_id']))
        # overwrite = discord.PermissionOverwrite()
        # overwrite.view_channel = False
        # await ctx.channel.set_permissions(user, overwrite=overwrite)
        # embed = discord.Embed(color=0x2f3136, description=f"Ticket Closed By {ctx.author.mention}")
        # await ctx.send(embed=embed)
    
    @commands.command(name="open", description="Open Current Ticket")
    @commands.check_any(checks.can_use())
    async def open(self, ctx):
        await ctx.send("This commands has moved to Slash Command", delete_after=10)
        # data = await self.bot.ticket.find_by_custom({'channel': ctx.channel.id, 'guild': ctx.guild.id})
        # if not data: return await ctx.send("Please use this command only in tickets")
        # user = ctx.guild.get_member(int(data['_id']))
        # overwrite = discord.PermissionOverwrite()
        # overwrite.view_channel = True
        # await ctx.channel.set_permissions(user, overwrite=overwrite)
        # embed = discord.Embed(color=0x2f3136, description=f"Ticket Opend By {ctx.author.mention}")
        # await ctx.send(content=f"<@{data['_id']}>",embed=embed)

    @commands.command(name="delete", description="delete the ticekt")
    @commands.check_any(checks.can_use())
    async def delete(self, ctx):
        await ctx.send("This commands has moved to Slash Command", delete_after=10)
        # data = await self.bot.ticket.find_by_custom({'channel': ctx.channel.id, 'guild': ctx.guild.id})

        # if not data: return await ctx.send("Please use this command only in tickets")

        # msg = await ctx.send("Deleting this Ticekt in 10s `type fs` to cancel this command")
        # try:
        #     stop_m = await self.bot.wait_for('message', check=lambda m: m.author.id == ctx.author.id and m.channel.id == ctx.channel.id and m.content.lower() == "fs", timeout=10)
        #     await stop_m.add_reaction("✅")
        #     return await msg.edit(content="Ok cancelling the command")
        # except asyncio.TimeoutError:
        #     await ctx.channel.delete()
        #     await self.bot.ticket.delete(data['_id'])

    @commands.command(name="transcript", description="Save current ticket's transcript", usage="[limit] [time Zone]", aliases=["save"])
    @commands.check_any(checks.can_use())
    async def transcript(self, ctx, limit: int = None, *, ticket=None):
        await ctx.send("This commands has moved to Slash Command", delete_after=10)
        # ticket = ticket if ticket else "Topic Not Given"

        # limit = limit if limit else 500
        # tz_info = "Asia/Kolkata"

        # data = await self.bot.ticket.find_by_custom({'channel': ctx.channel.id, 'guild': ctx.guild.id})
        # embed = discord.Embed(description=f"{ctx.author.mention} by Pressing bellow button your allowing as to save messages of this channel")
        # m = await ctx.send(content="Saving Started",embed=None,view=None)
        # channel = self.bot.get_channel(833386438338674718)
        # transcript = await chat_exporter.export(ctx.channel, limit, tz_info)
        # if transcript is None:
        #     return
        # transcript_file = discord.File(io.BytesIO(transcript.encode()),filename=f"transcript-{ctx.channel.name}.html")

        # link_msg = await channel.send(f"{ctx.channel.name} | {ticket}", file=transcript_file)

        # link_button = discord.ui.View()
        # url = f"https://codebeautify.org/htmlviewer?url={link_msg.attachments[0].url}"
        # link_button.add_item(discord.ui.Button(label='View Transcript', url=url))

        # await link_msg.edit(view=link_button)
        # await m.edit(content=f"{ctx.author.mention} transcript Saved",)

        # channel_file = discord.File(io.BytesIO(transcript.encode()),
        #                             filename=f"transcript-{ctx.channel.name}.html")
        # await ctx.send(f"{ctx.channel.name} | {ticket}", file=channel_file, view=link_button)
    
    @commands.command(name="add", description="add User to the channel", usage="[member]")
    @commands.check_any(checks.can_use())
    async def add(self, ctx, *, target: Union[discord.Member, discord.Role]):
        await ctx.send("This commands has moved to Slash Command", delete_after=10)
        # channel = ctx.channel
        # if ctx.channel.category.id == 829230513516445736:

        #     overwrite = channel.overwrites_for(target)
        #     overwrite.view_channel = True
        #     overwrite.send_messages = True

        #     await channel.set_permissions(target, overwrite=overwrite)
        #     embed = discord.Embed(
        #         description=f"<:allow:819194696874197004> | Added {target.mention} to the Ticket")

        #     await ctx.send(embed=embed)

    @commands.command(name="remove", description="Remove User to the channel", usage="[member]")
    @commands.check_any(checks.can_use())
    async def remove(self, ctx, *, target: Union[discord.Member, discord.Role]):
        await ctx.send("This commands has moved to Slash Command", delete_after=10)
        # channel = ctx.channel
        # if ctx.channel.category.id == 829230513516445736:

        #     overwrite = channel.overwrites_for(target)
        #     overwrite.view_channel = False
        #     overwrite.send_messages = False

        #     await channel.set_permissions(target, overwrite=overwrite)
        #     embed = discord.Embed(
        #         description=f"<:allow:819194696874197004> | Removed {target.mention} to the Tick")

        #     await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Tickets(bot))

## NEw System Draft
# class ticket_class(discord.ui.View):
#     def __init__(self):
#         super().__init__(timeout=None)
    
#     @discord.ui.button(label='Server Support', style=discord.ButtonStyle.red, custom_id='ticket:red', emoji="<:support:837272254307106849>")
#     async def support(self, button: discord.ui.Button, interaction: discord.Interaction):
#         await interaction.response.send_message("This Should Create New ticket", ephemeral=True)
    
#     @discord.ui.button(label='Partnership ', style=discord.ButtonStyle.green, custom_id='ticket:partner_ship', emoji="<:partner:837272392472330250>")
#     async def partnership(self, button: discord.ui.Button, interaction: discord.Interaction):
#         await interaction.response.send_message("This Should Create New ticket", ephemeral=True)

# class PersistentView(discord.ui.View):
#     def __init__(self):
#         super().__init__(timeout=None)

#     @discord.ui.select(placeholder="Select Your Qestion from Below", max_values=1, min_values=1,custom_id="ticket:select",
#         options=[discord.SelectOption(label="Weekly Amari Rewards?", value="0"),
#                 discord.SelectOption(label="Perks for Voting", value="1"),
#                 discord.SelectOption(label="become a Staff Member?", value="2"),
#                 discord.SelectOption(label="I have Other Qestions", value="ticket")])
#     async def select(self, select: discord.ui.select, interaction: discord.Interaction):
#         print(select.values)
#         if select.values[0] == str(0):
#             amari_embed = discord.Embed(title="What are Weekly Amari Rewards?", description="Members gain Amaari XP by engaging on the server through text, audio and bot channels. Top 3 Members, with the highest XP, are rewarded every week with:\n✦ Special <@&787566907833581590> role\n✦ Access Dank Memer Premium with 3x Amari\n✦ Guild wide 2x Amari\n✦ Free DMC as per rank:",color=0xffd700)
#             amari_embed.add_field(name="Winner", value="🥇 ⏣ 1,500,000")
#             amari_embed.add_field(name="Runner-up", value="🥈 ⏣ 1,000,000")
#             amari_embed.add_field(name="Second Runner-up", value="🥉 ⏣ 500,000")
#             amari_embed.set_footer(text="The Gambler's Kingdom", icon_url="https://cdn.discordapp.com/icons/785839283847954433/a_23007c59f65faade4c973506d9e66224.gif?size=1024")
#             await interaction.response.send_message(embed=amari_embed, ephemeral=True)
#         elif select.values[0] == str(1):
#             vote_embed = discord.Embed(title="What perks will I gain by voting for the server?", description="You can vote for The Gambler's Kingdom here every 12 Hours, and for every 12 Hours you get the following perks:\n✦ Special temporary <@&786884615192313866> role\n✦ 2,500 Casino Cash. Collect using ,collect-income in <#786117471840895016>\n✦ Access to Dank Memer Premium with 2x Amari\n✦ Guild wide 2x Amaari\n\nTo access the vote link anywhere on the server, simply use Vote Link.",color=0xffd700)
#             vote_embed.set_footer(text="The Gambler's Kingdom", icon_url="https://cdn.discordapp.com/icons/785839283847954433/a_23007c59f65faade4c973506d9e66224.gif?size=1024")
#             view = discord.ui.View()
#             view.add_item(discord.ui.Button(label='Click Here', url="https://top.gg/servers/785839283847954433/vote"))
#             await interaction.response.send_message(embed=vote_embed, ephemeral=True, view=view)
#         elif select.values[0] == str(2):
#             staff_embed = discord.Embed(description='Check <#839388341627912242> for staff applications',color=0xffd700)
#             staff_embed.set_footer(text="The Gambler's Kingdom", icon_url="https://cdn.discordapp.com/icons/785839283847954433/a_23007c59f65faade4c973506d9e66224.gif?size=1024")
#             await interaction.response.send_message(embed=staff_embed, ephemeral=True)
#         elif select.values[0].lower() =="ticket":
#             await interaction.response.send_message("Press Below Button to Make Ticket", view=ticket_class(), ephemeral=True)

# class test(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
    
#     @commands.Cog.listener()
#     async def on_ready(self):
#         self.bot.add_view(PersistentView())
#         self.bot.add_view(ticket_class())
#         print(f'{self.__class__.__name__} Cog has been loaded\n-----')
    
#     @commands.command()
#     async def faq(self, ctx):
#         embed = discord.Embed(title="Support Centre",description="This channel is for in-server support purpose only, talking anything here which is not related to the channel usage will result in warn or mute, mini-modding is also not allowed, we have enough staff members to handle it. Thank you for your cooperation.",color=0xff0000)
#         embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
#         await ctx.send(embed=embed, view=PersistentView())

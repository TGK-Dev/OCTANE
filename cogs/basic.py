import discord
from discord.ext import commands
from discord import app_commands
from typing import Literal
from utils.checks import Commands_Checks
import time
import datetime
class Basic(commands.Cog, name="Basic", description="General Basic Commands"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded")
    
    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        if before.guild.id != 785839283847954433: return
        if len(after.activities) <= 0: 
            role = discord.utils.get(after.guild.roles, id=992108093271965856)
            if role in after.roles:
                await after.remove_roles(role)
            return
        for activity in after.activities:
            try:
                if activity.type == discord.ActivityType.custom:
                    if ".gg/tgk" in activity.name.lower():
                        role = discord.utils.get(after.guild.roles, id=992108093271965856)
                        await after.add_roles(role)
                        return
                    elif not ".gg/tgk" in activity.name.lower():
                        role = discord.utils.get(after.guild.roles, id=992108093271965856)
                        if role in after.roles:
                            await after.remove_roles(role)
                        return
            except:
                pass
        
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return
        if message.content.startswith("gk") or message.content.startswith(">") or message.content.startswith("?"):
            return
        self.bot.snipe['delete'][message.channel.id] = {'id': message.id, 'content': message.content, 'author': message.author.id}
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot:
            return
        if before.content.startswith("gk") or before.content.startswith(">") or before.content.startswith("?"):
            return
        self.bot.snipe['edit'][before.channel.id] = (before.content, after.content)
    
    @app_commands.command(name="ping", description="Show's the bot's latency")
    async def ping(self, interaction: discord.Interaction):
        start_time = time.time()
        await interaction.response.send_message("Pong!")
        end_time = time.time()

        dstart = datetime.datetime.utcnow()
        await self.bot.config.find(interaction.guild.id)
        dend = datetime.datetime.utcnow()
        dping = (dend - dstart)
        dping = dping.total_seconds()

        await interaction.edit_original_response(content=f"**Response TIme** {round(self.bot.latency * 1000)}ms\n**API**: {round((end_time - start_time) * 1000)}ms\n**Database Ping**: {round(dping * 1000)}Ms\n**Last Reboot**: <t:{round(self.bot.uptime.timestamp())}:R>")
    
    @app_commands.command(name="snipe", description="Snipe the message in current channel")
    @app_commands.guilds(785839283847954433)
    @app_commands.describe(type="Select a type of snipe")
    async def snipe(self, interaction: discord.Interaction, type: Literal['delete', 'edit'], hidden: bool):
        if type == 'delete':

            message_data = self.bot.snipe['delete'].get(interaction.channel.id)
            if message_data is None:
                await interaction.response.send_message("No message to snipe", ephemeral=True)
                return

            message_author = self.bot.get_user(message_data['author'])

            embed = discord.Embed(color=interaction.user.color)
            embed.set_author(name=message_author.name, icon_url=message_author.avatar.url)
            embed.description = message_data['content']
            embed.set_footer(text=f"Sniped by {interaction.user.name}")

            await interaction.response.send_message(embed=embed, ephemeral=hidden)
        
        elif type == 'edit':
            message_data = self.bot.snipe['edit'].get(interaction.channel.id)
            if message_data is None:
                await interaction.response.send_message("No message to snipe", ephemeral=hidden)
                return
            embed = discord.Embed(color=interaction.user.color)
            embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url)
            embed.description = f"**Before:** {message_data[0]}\n**After:** {message_data[1]}"
            embed.set_footer(text=f"Sniped by {interaction.user.name}")
            await interaction.response.send_message(embed=embed, ephemeral=hidden)
    
        
    @app_commands.command(name="enter", description="Tell everyone that you enter the chat")
    async def enter(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"**{interaction.user}** has entered the room! <:TGK_pepeenter:790189012148682782>")
    
    @app_commands.command(name="exit", description="Tell everyone that you leave the chat")
    async def exit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"**{interaction.user}** has left the room! <:TGK_pepeexit:790189030569934849>")

    @commands.command(name="vote", description="Vote for a server", brife="vote")
    async def vote(self, ctx):
        await ctx.message.delete()
        tgk = self.bot.get_guild(785839283847954433)
        embed = discord.Embed(
                title=f"<a:tgk_redcrown:1005473874693079071> {tgk.name}", 
                description= f"<:tgk_redarrow:1005361235715424296> `+1x` amari guild-wide\n"
                f"<:tgk_redarrow:1005361235715424296> Access to [**Special Channel**](https://discord.com/channels/785839283847954433/929613393097293874)\n"
                f"<:tgk_redarrow:1005361235715424296> `+1x` entry in <@700743797977514004>'s gaws\n", 
                color=0xff0000,
                url="https://top.gg/servers/785839283847954433/vote"
                )
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label=f'Top.gg', url="https://top.gg/servers/785839283847954433/vote"))
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Basic(bot))

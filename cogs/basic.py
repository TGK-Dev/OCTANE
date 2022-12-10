import discord
from discord.ext import commands
from discord import app_commands
from typing import Literal
from utils.checks import Commands_Checks, Dynamic_cooldown
from ui.buttons import level_check
import time
import datetime
import asyncio
import aiohttp
from amari import AmariClient
class Basic(commands.Cog, name="Basic", description="General Basic Commands"):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.bot.Amari_api = AmariClient(bot.Amari_token)
        self.bot.presence_chache = {}
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(level_check(self.bot))

        for afk in await self.bot.afk.get_all(): self.bot.current_afk[afk['_id']] = afk        
        print(f"{self.__class__.__name__} Cog has been loaded")
    
    @commands.Cog.listener()
    async def on_presence_update(self, before, after):
        if before.guild.id != 785839283847954433: return
        supporter_role = before.guild.get_role(992108093271965856)
        supporter_log_channel = before.guild.get_channel(1031514773310930945)
        if len(after.activities) <= 0 and supporter_role in after.roles:
            await after.remove_roles(supporter_role, reason="No longer supporting")
            return        
        await asyncio.sleep(5)

        for activity in after.activities:
            try:
                if activity.type == discord.ActivityType.custom:
                    if ".gg/tgk" in activity.name.lower():

                        if supporter_role in after.roles: return
                        embed = discord.Embed(description=f"Thanks for supporting the The Gambler's Kingdom\n\nYou have been given the {supporter_role.mention} role", color=supporter_role.color)
                        embed.set_author(name=f"{after.name}#{after.discriminator} ({after.id})", icon_url=after.avatar.url if after.avatar else after.default_avatar)
                        embed.set_footer(text=self.bot.user.name, icon_url=self.bot.user.avatar.url)
                        embed.timestamp = datetime.datetime.now()
                        embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/869579480509841428.gif?v=1")
                        await supporter_log_channel.send(embed=embed)
                        await after.add_roles(supporter_role)
                        return

                    elif not ".gg/tgk" in activity.name.lower():
                        
                        if supporter_role in after.roles: await after.remove_roles(supporter_role)                        
                        return
            except Exception as e:
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

    @app_commands.command(name="level")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.guilds(785839283847954433, 811037093715116072)
    async def level(self, interaction: discord.Interaction):
        embed = discord.Embed(description="Click Below Button To Check Level", color=0xADD8E6)
        await interaction.response.send_message(embed=embed, view=level_check(self.bot))

class AFK(commands.Cog, name="AFK", description="Member Afk Module"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.guild is None:
            return
        
        if message.guild.id != 785839283847954433: return
        if message.author.id in self.bot.current_afk.keys():
            try:
                await message.author.edit(nick=self.bot.current_afk[message.author.id]['last_name'])
            except discord.Forbidden:
                pass
            await message.reply(f"Welcome back! I have removed your AFK status, {self.bot.current_afk[message.author.id]['total_afk']} people pinged you while you were AFK")
            await self.bot.afk.delete(message.author.id)
            del self.bot.current_afk[message.author.id]
        
        if len(message.mentions) > 0:
            for user in message.mentions:
                if user.id in self.bot.current_afk.keys():
                    afk = self.bot.current_afk[user.id]
                    await message.reply(f"{user.mention} is AFK Since <t:{afk['time']}:R>\nReason: {afk['message']}", delete_after=10, allowed_mentions=discord.AllowedMentions(users=False, roles=False, everyone=False))
                    data = await self.bot.afk.find(user.id)
                    data['total_afk'] += 1
                    await self.bot.afk.upsert(data)
                    self.bot.current_afk[user.id] = data
        
        if message.interaction != None:
            interaction = message.interaction
            if interaction.user.id in self.bot.current_afk.keys():
                try:
                    await interaction.user.edit(nick=self.bot.current_afk[interaction.user.id]['last_name'])
                except discord.Forbidden:
                    pass
                await message.reply(f"Welcome back! I have removed your AFK status {self.bot.current_afk[interaction.user.id]['total_afk']} people pinged you while you were AFK")
                await self.bot.afk.delete(interaction.user.id)
                del self.bot.current_afk[interaction.user.id]

    @app_commands.command(name="afk", description="Set your AFK status")
    @app_commands.guilds(785839283847954433)
    @app_commands.describe(status="Your AFK reason")
    @app_commands.checks.dynamic_cooldown(Dynamic_cooldown.is_me)
    async def afk(self, interaction: discord.Interaction, status: str = None):
        afk_data = await self.bot.afk.find(interaction.user.id)
        if afk_data:
            await interaction.response.send_message("You are already afk", ephemeral=True)
            return

        afk_data = {'_id':interaction.user.id, 'message': status, 'last_name': interaction.user.display_name,'time': round(discord.utils.utcnow().timestamp()), 'total_afk': 0}
        await self.bot.afk.insert(afk_data)

        await interaction.response.send_message(f"Set your AFK status to: {status}", ephemeral=True)
        try:
            await interaction.user.edit(nick=f"{interaction.user.display_name} [AFK]")
        except:
            pass
        
        self.bot.current_afk[interaction.user.id] = afk_data

    @afk.error
    async def afk_error(self, interaction: discord.Interaction, error):
        print(error)
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(f"Please wait {round(int(error.retry_after))} seconds before using this command again", ephemeral=True)
    

async def setup(bot):
    await bot.add_cog(Basic(bot))
    await bot.add_cog(AFK(bot))

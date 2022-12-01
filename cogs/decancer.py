import asyncio
import random
import re
import unicodedata
import discord
import stringcase
import unidecode
from datetime import datetime, timedelta
from discord.ext import commands
from discord import app_commands
from utils.db import Document        

class Decancer(commands.GroupCog, description="Fix Member name on Join", name="decancer"):
    def __init__(self, bot):
        self.bot = bot
        self.bot.decancer = Document(self.bot.db, "decancer")
    
    @app_commands.command(name="user", description="decancer user")
    @app_commands.describe(user="user to decancer")
    @app_commands.checks.has_permissions(manage_nicknames=True)
    async def user(self, interaction: discord.Interaction, user: discord.Member):
        old_name = user.display_name
        is_cancerous = self.is_cancerous(old_name)
        if is_cancerous:
            new_name = await self.nick_maker(interaction.guild, old_name)
            await user.edit(nick=new_name, reason=f"user decancer by {interaction.user.name}")
            embed = discord.Embed(description=f"{user.mention}'s name has been decancerd", color=discord.Color.blue())
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(description=f"{user.mention}'s name is not cancerous", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="server", description="decancer server")
    @app_commands.checks.has_permissions(administrator=True)
    async def server(self, interaction: discord.Interaction):
        embed = discord.Embed(description="Decancering server in below thread", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)
        data = await interaction.client.find(interaction.guild.id)

        message = await interaction.original_response()
        thread = await message.create_thread(name="decancer-log", auto_archive_duration=60)

        async with thread.typing():
            for member in interaction.guild.members:
                roles = [role.id for role in member.roles]
                bypass = data['bypass']
                if bypass in roles: continue
                old_name = member.display_name
                is_cancerous = self.is_cancerous(old_name)
                if is_cancerous:
                    new_name = await self.nick_maker(interaction.guild, old_name)
                    await thread.send(f"{member.mention} name changed from {old_name} to {new_name}")
                    await member.edit(nick=new_name, reason=f"Server decancer started by {interaction.user.name}")
                    
        embed.description = "Decancering server complete"
        await interaction.edit_original_response(embed=embed)
    
    @app_commands.command(name="bypass", description="set bypass for decancer")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(role="user to bypass")
    async def bypass(self, interaction: discord.Interaction, role: discord.Role):
        data = await interaction.client.decancer.find(interaction.guild.id)
        if not data:
            data = {"_id": interaction.guild.id, "bypass": []}
            await interaction.client.decancer.insert(data)
        if role.id not in data["bypass"]:
            data["bypass"].append(role.id)
            await interaction.client.decancer.update(data)
            embed = discord.Embed(description=f"{role.mention} has been added to the bypass list", color=discord.Color.blue())
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(description=f"{role.mention} is already in the bypass list", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="unbypass", description="remove bypass for decancer")
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(role="user to unbypass")
    async def unbypass(self, interaction: discord.Interaction, role: discord.Role):
        data = await interaction.client.decancer.find(interaction.guild.id)
        if not data:
            data = {"_id": interaction.guild.id, "bypass": []}
            await interaction.client.decancer.insert(data)
        if role.id in data["bypass"]:
            data["bypass"].remove(role.id)
            await interaction.client.decancer.update(data)
            embed = discord.Embed(description=f"{role.mention} has been removed from the bypass list", color=discord.Color.blue())
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(description=f"{role.mention} is not in the bypass list", color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
    
    async def on_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        try:
            await interaction.response.send_message(error, ephemeral=True)
        except discord.InteractionResponded:
            await interaction.followup.send(error, ephemeral=True)
        except:
            pass

    @staticmethod
    def is_cancerous(text: str) -> bool:
        for segment in text.split():
            for char in segment:
                if not (char.isascii() and char.isalnum()):
                    return True
        return False
    
    @staticmethod
    def strip_accs(text):
        try:
            text = unicodedata.normalize("NFKC", text)
            text = unicodedata.normalize("NFD", text)
            text = unidecode.unidecode(text)
            text = text.encode("ascii", "ignore")
            text = text.decode("utf-8")
        except Exception as e:
            print(e)
        return str(text)
    
    async def nick_maker(self, guild: discord.Guild, old_shit_nick):
        old_shit_nick = self.strip_accs(old_shit_nick)
        new_cool_nick = re.sub("[^a-zA-Z0-9 \n.]", "", old_shit_nick)
        new_cool_nick = " ".join(new_cool_nick.split())
        new_cool_nick = stringcase.lowercase(new_cool_nick)
        new_cool_nick = stringcase.titlecase(new_cool_nick)
        default_name = "Request a new name"
        if len(new_cool_nick.replace(" ", "")) <= 1 or len(new_cool_nick) > 32:
            if default_name == "random":
                new_cool_nick = await self.get_random_nick(2)
            elif default_name:
                new_cool_nick = default_name
            else:
                new_cool_nick = "simp name"
        return new_cool_nick
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return

        guild: discord.Guild = member.guild
        old_nick: str = member.display_name

        if not self.is_cancerous(old_nick):
            return
        await asyncio.sleep(5)
        member = guild.get_member(member.id)

        if not member:
            return
        
        if member.top_role >= guild.me.top_role:
            return
        
        new_nick: str = await self.nick_maker(guild, old_nick)
        if old_nick.lower() != new_nick.lower():
            try:
                await member.edit(nick=new_nick, reason="Auto Decancer")
            except discord.NotFound:
                pass
            except discord.Forbidden:
                pass

async def setup(bot):
    await bot.add_cog(Decancer(bot), guilds=[discord.Object(785839283847954433)])
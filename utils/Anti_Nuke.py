import discord
import asyncio
import aiohttp
from discord.ext import commands
from discord import Webhook
import os

class Anti_Nuke():
    def __init__(self, bot: commands.Bot, user: discord.Member, target: discord.Member, role: discord.Role, reason:str):
        self.bot = bot
        self.user = user
        self.reason = reason
        self.target = target
        self.role = role
    
    async def quarantine(bot: commands.Bot, user: discord.Member, target: discord.Member, role: discord.Role, reason: str):
        embed = discord.Embed(title="Quarantined", description=f"{user.mention} has been quarantined for {reason}.", color=0xFF0000)
        embed.timestamp = discord.utils.utcnow()
        embed.set_thumbnail(url=user.avatar.url)
        embed.timestamp = discord.utils.utcnow()
        
        with open("Nuke_role_remove_log.txt", "w") as file:
            for role in user.roles:
                try:
                    await user.remove_roles(role, reason="Quarantined")        
                    file.write(f"Removed: {int(role.id)}\n")
                except:
                    file.write(f"Failed to remove: {int(role.id)}\n")
            file.close()

        quarantine_role = discord.utils.get(user.guild.roles, name="Quarantined")
        if not quarantine_role:
            quarantine_role = await user.guild.create_role(name="Quarantined")
            override = discord.PermissionOverwrite()
            override.send_messages = False
            override.read_messages = False
            override.read_message_history = False
            override.view_channel = False
            for channel in user.guild.text_channels:
                await channel.set_permissions(quarantine_role, overwrite=override)
        
        await user.add_roles(quarantine_role, reason="Quarantined")

        with open("Nuke_role_remove_log.txt", "rb") as file:

            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(bot.nuke_webhook, session=session)
                await webhook.send(embed=embed, username=f"{bot.user.name} Anti-Nuke", avatar_url=bot.user.avatar.url, content="`@everyone`", file=discord.File(file, filename=f"User ID: {user.id} Role Logs.txt"))
                file.truncate(0)
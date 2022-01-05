import re
import discord
import asyncio
import datetime
from discord import channel
from discord.ext import commands
from discord.ext.commands.core import command
from utils.exceptions import IdNotFound

class starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_read(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not payload.guild_id:
            return
        entries = await self.bot.config.get_all()
        guilds = list(map(lambda e: e["_id"], entries))
        if payload.guild_id in guilds:
            guild = list(filter(lambda e: e["_id"] == payload.guild_id, entries))
            guild = guild[0]
            emoji = "⭐"
        if not guild.get("starboard_channel"): return    
        if not guild.get("starboard_toggle", True): return
        if not str(payload.emoji) == "⭐": return
        channel = self.bot.get_channel(payload.channel_id)
        try:
            msg = await channel.fetch_message(payload.message_id)
            reacts = msg.reactions
            reacts = list(filter(lambda r: str(r.emoji) == "⭐", reacts))
        except discord.HTTPException:
            pass

        if reacts:
            react = list(map(lambda u: u.id, await reacts[0].users().flatten()))
            if msg.author.id in react:
                del react[react.index(msg.author.id)]
            
            thresh = guild.get("emoji_threshold") or 7
            if len(react) >= thresh:
                starboard_channel = self.bot.get_channel(guild["starboard_channel"])
                try:
                    existing_star = await self.bot.starboard.find_by_custom(
                                    {
                                        "_id": payload.message_id,
                                        "guildId": payload.guild_id,
                                        "channelId": payload.channel_id,
                                    }
                                )
                except IdNotFound:
                    pass
                
                else:
                    if not existing_star:
                        pass
                    else:
                        existing_message = await starboard_channel.fetch_message(existing_star["starboard_message_id"])
                        return await existing_message.edit(content=f":dizzy: {len(react)} | {channel.mention}",embed=existing_message.embeds[0])
                                            
                if channel == starboard_channel: return

                embed = discord.Embed(color=0x9e3bff, timestamp=datetime.datetime.now())
                embed.set_author(name=f"{msg.author.display_name}",icon_url=msg.author.avatar.url)
                embed.set_footer(text=f"ID: {msg.id}")
                embed.add_field(name="Message", value=msg.content, inline=False)
                embed.add_field(name="Original", value=f"[Jump!]({msg.jump_url})", inline=False)
                if msg.reference:
                    reply_to = await channel.fetch_message(msg.reference.message_id)
                    if not reply_to:
                        pass
                    else:
                        embed.add_field(name="Replying to...", value=f"[{reply_to.content}]({reply_to.jump_url})", inline=False)
                
                attach = msg.attachments[0] if msg.attachments else None
                if attach:
                    embed.set_image(url=attach.url)
                
                starboard_message =  await starboard_channel.send(content=f":dizzy: {len(react)} | {channel.mention}",embed=embed)
                await starboard_message.add_reaction("⭐")
                await self.bot.starboard.upsert(
                    {"_id": payload.message_id,
                    "guildId": payload.guild_id,
                    "authorId": payload.user_id,
                    "channelId": payload.channel_id,
                    "starboard_message_id": starboard_message.id,}
                )

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if not payload.guild_id: return
        entries = await self.bot.config.get_all()
        guilds = list(map(lambda e: e["_id"], entries))
        if payload.guild_id in guilds:
            guild = list(filter(lambda e: e["_id"] == payload.guild_id, entries))
            guild = guild[0]
            emoji = "⭐"
        
        if not guild.get("starboard_channel"): return

        if not guild.get("starboard_toggle", True): return

        if str(payload.emoji) == emoji:
            channel = self.bot.get_channel(payload.channel_id)
            try:
                msg = await channel.fetch_message(payload.message_id)
                reacts = msg.reactions
                reacts = list(filter(lambda r: str(r.emoji) == emoji, reacts))
            except discord.HTTPException:
                pass
            
            if reacts:
                react = list(map(lambda u: u.id, await reacts[0].users().flatten()))
                if msg.author.id in react:
                    del react[react.index(msg.author.id)]

                thresh = guild.get("emoji_threshold") or 7
                if len(react) >= thresh:
                    starboard = self.bot.get_channel(guild["starboard_channel"])
                    try:
                        existing_star = await self.bot.starboard.find_by_custom(
                            {
                                "_id": payload.message_id,
                                "guildId": payload.guild_id,
                                "channelId": payload.channel_id,
                            }
                        )
                    except IdNotFound:
                        return
                    else:
                        if not existing_star.get("starboard_message_id"):
                            return
                        existing_message = await starboard.fetch_message(existing_star["starboard_message_id"])
                        return await existing_message.edit(content=f":dizzy: {len(react)} | {channel.mention}",embed=existing_message.embeds[0])

    @commands.group(invoke_without_command=True,description="Config command for startbord module")
    async def starboard(self, ctx):
        data = await self.bot.config.find(ctx.guild.id)
        embed = discord.Embed(title=f"{ctx.guild.name}'s Startbord Config",color=0x9e3bff,
        description=f"\nStartbord Toggle: {data['starboard_toggle']}\nStarbord Channel: <#{data['starboard_channel']}>\nStartboard Threshold: {data['emoji_threshold']}")
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
        await ctx.send(embed=embed)
    
    @starboard.group(invoke_without_command=True, name="threshold")
    async def threshold(self, ctx, threshold: int=None):
        data = await self.bot.config.find(ctx.guild.id)
        if not data: return await ctx.send("No config found")
        if threshold:
            data['emoji_threshold'] = threshold
            await ctx.send(f"New Threshhold is {threshold}")
            await self.bot.config.upsert(data)
        if not threshold:
            await ctx.send(f"Current Threshhold is {data['emoji_threshold']}")

    @starboard.group(invoke_without_command=True, name="toggle")
    async def toggle(self, ctx, toggle: bool=False):
        data = await self.bot.config.find(ctx.guild.id)
        if not data: return await ctx.send("No config found")
        if toggle:
            data['starboard_toggle'] = toggle
            await ctx.send(f"Starboard is {toggle}")
            await self.bot.config.upsert(data)
        if not toggle:
            await ctx.send(f"Current status is {data['starboard_toggle']}")

    @starboard.group(invoke_without_command=True, name="channel")
    async def channel(self, ctx, channel: discord.TextChannel=None):
        data = await self.bot.config.find(ctx.guild.id)
        if not data: return await ctx.send("No config found")
        if channel:
            data['starboard_channel'] = channel.id
            await ctx.send(f"New starboard is {channel.mention}")
            await self.bot.config.upsert(data)
        if not channel:
            await ctx.send(f"Current starboard channel is <#{data['starboard_channel']}>")

def setup(bot):
    bot.add_cog(starboard(bot))
    
"""
    create_option(name="toggle", description="Toggle the starbord", required=False, option_type=5),
        create_option(name="threshold", description="Set threshhold for the reactions", required=False, option_type=4),
        create_option(name="channel", description="Set Channel for Starbord", required=False, option_type=7),
    ])
"""

            

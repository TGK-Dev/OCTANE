from discord import Interaction
from discord.ext import commands
from discord import app_commands
import discord
import datetime
from utils.checks import Commands_Checks
class Starboard(commands.Cog, name="Starboard", description="Starboard Module"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not payload.guild_id:
            return

        if payload.message_id in self.bot.bot_temp_star: return
        
        guild = self.bot.get_guild(payload.guild_id)
        channel = self.bot.get_channel(payload.channel_id)
        try:
            message = await channel.fetch_message(payload.message_id)
            reacts = list(filter(lambda r: str(r.emoji) == "⭐", message.reactions))
        except discord.NotFound:
            return
        
        self.bot.bot_temp_star[message.id] = {'message': message.id, 'channel': channel.id, 'guild': guild.id}

        if not reacts: return
        guild_data = await self.bot.config.find(guild.id)
        reacts = [user.id async for user in reacts[0].users()]

        if message.author.id in reacts and guild_data['starboard']['self_star'] == False:
            del reacts[reacts.index(message.author.id)]
        
        if len(reacts) >= int(guild_data['starboard']['threshold']):
            starboard_channel = guild.get_channel(int(guild_data['starboard']['channel']))
            if channel.id == starboard_channel.id: return
            try:
                existing_star = await self.bot.starboard.find_by_custom(
                    {
                        '_id': message.id, "guildId": guild.id, "channelId": channel.id
                    })
            except:
                pass

            else:
                if not existing_star:
                    pass
                else:
                    existing_star_messae = await starboard_channel.fetch_message(existing_star['starboard_message_id'])
                    return await existing_star_messae.edit(content=f":dizzy: {len(reacts)} | {channel.mention}")

            star_message_embed = discord.Embed(color=0x9e3bff, timestamp=discord.utils.utcnow())
            try:
                star_message_embed.set_author(name=f"{message.author}", icon_url=message.author.avatar.url)
            except AttributeError:
                star_message_embed.set_author(name=f"{message.author}", icon_url=message.author.default_avatar)
            star_message_embed.set_footer(text=f"{message.id}")
            if message.content:
                star_message_embed.add_field(name="Message", value=message.content, inline=False)
            star_message_embed.add_field(name="Original", value=f"[Jump!]({message.jump_url})", inline=False)
            if message.reference:
                reply_to = await channel.fetch_message(message.reference.message_id)
                if reply_to:
                    star_message_embed.add_field(name="Replying to ...", value=f"[{reply_to.content}]({reply_to.jump_url})", inline=False)
                else:
                    pass
            extra_embed = [star_message_embed]
            if len(message.attachments) > 0:                
                for attachment in message.attachments:
                    image_embed = discord.Embed(color=0x9e3bff).set_image(url=attachment.url)
                    extra_embed.append(image_embed)
            starborad_sent_message = await starboard_channel.send(content=f":dizzy:{len(reacts)} | {channel.mention}", embeds=extra_embed)
            await starborad_sent_message.add_reaction("⭐")

            await self.bot.starboard.insert({
                '_id': message.id,
                'guildId': guild.id,
                'authorId': message.author.id,
                'channelId': channel.id,
                'starboard_message_id': starborad_sent_message.id,
            })
            try:
                self.bot.bot_temp_star.pop(message.id)
            except KeyError:
                pass
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if not payload.guild_id: return
        guild = self.bot.get_guild(payload.guild_id)
        guild = await self.bot.config.find(guild.id)
        emoji = "⭐"

        if not guild['starboard']['channel']: return
        channel = self.bot.get_channel(payload.channel_id)

        try:
            message = await channel.fetch_message(payload.message_id)
            reacts = message.reactions
            reacts = list(filter(lambda r: str(r.emoji) == "⭐", message.reactions))

        except discord.HTTPException:
            return
        
        if reacts:
            react = [user async for user in reacts[0].users()]
            if message.author in react and guild['starboard']['self_star'] == False:
                del react[react.index(message.author)]

            starboard = self.bot.get_channel(guild['starboard']['channel'])
            try:
                existing_star = await self.bot.starboard.find_by_custom(
                    {
                        "_id": payload.message_id,
                        "guildId": payload.guild_id,
                        "channelId": payload.channel_id,
                    }
                )
            except:
                return
            else:
                if not existing_star.get("starboard_message_id"):
                    return
                existing_message = await starboard.fetch_message(existing_star["starboard_message_id"])
                return await existing_message.edit(content=f":dizzy: {len(react)} | {channel.mention}")

    @commands.group(invoke_without_command=True, description="Config command for startbord module", brife="config")
    @commands.check_any(Commands_Checks.can_use())
    async def starboard(self, ctx):
        guild_data = await self.bot.config.find(ctx.guild.id)
        embed = discord.Embed(title=f"{ctx.guild.name}'s Startbord Config",color=0x9e3bff)
        data = guild_data['starboard']
        embed.description=f"\nStartbord Toggle: {data['toggle']}\nStarbord Channel: <#{data['channel']}>\nStartboard Threshold: {data['threshold']}\nStarboard Self Star: {data['self_star']}"
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
        await ctx.send(embed=embed)
    
    @starboard.command(name="toggle", description="Toggle starboard on/off", brief="toggle [True/False]")
    @commands.check_any(Commands_Checks.can_use(), Commands_Checks.is_owner())
    async def starboard_toggle(self, ctx, toggle: bool=True):
        guild_data = await self.bot.config.find(ctx.guild.id)
        guild_data['starboard']['toggle'] = toggle
        await self.bot.config.update(ctx.guild.id, guild_data)
        await ctx.send(f"Starboard toggle set to {toggle}")
    
    @starboard.command(name="channel", description="Set starboard channel", brief="channel [channel]")
    @commands.check_any(Commands_Checks.can_use(), Commands_Checks.is_owner())
    async def starboard_channel(self, ctx, channel: discord.TextChannel):
        guild_data = await self.bot.config.find(ctx.guild.id)
        guild_data['starboard']['channel'] = channel.id
        await self.bot.config.update(ctx.guild.id, guild_data)
        await ctx.send(f"Starboard channel set to <#{channel.id}>")
    
    @starboard.command(name="threshold", description="Set starboard threshold", brief="threshold [threshold]")
    @commands.check_any(Commands_Checks.can_use(), Commands_Checks.is_owner())
    async def starboard_threshold(self, ctx, threshold: int=5):
        guild_data = await self.bot.config.find(ctx.guild.id)
        guild_data['starboard']['threshold'] = threshold
        await self.bot.config.update(ctx.guild.id, guild_data)
        await ctx.send(f"Starboard threshold set to {threshold}")
    
    @starboard.command(name="selfstar", description="Toggle starboard self star", brief="selfstar [True/False]")
    async def starboard_selfstar(self, ctx, toggle: bool=False):
        guild_data = await self.bot.config.find(ctx.guild.id)
        guild_data['starboard']['self_star'] = toggle
        await self.bot.config.update(ctx.guild.id, guild_data)
        await ctx.send(f"Starboard self star set to {toggle}")

async def setup(bot):
    await bot.add_cog(Starboard(bot))
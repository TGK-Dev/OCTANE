from discord import Interaction
from discord.ext import commands
from discord import app_commands
import discord
import datetime
from utils.checks import Commands_Checks
from ui.poll import make_poll
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
        if payload.guild_id != 785839283847954433:
            return
        if payload.emoji.name != "⭐":
            return
        if payload.message_id in self.bot.temp_star:
            return        
        config = await self.bot.config.find(payload.guild_id)
        if not config:
            return
        if config['starboard']['toggle'] == False:
            return
        if payload.channel_id == config['starboard']['channel']:
            return
        try:
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
        except discord.NotFound:
            return
        
        reaction = []
        for reactions in message.reactions:

            if reactions.emoji == "⭐":
                reaction = [user.id async for user in reactions.users()]
                break
        if len (reaction) == 0:
            return

        if config['starboard']['self_star'] == True:
            pass
        elif config['starboard']['self_star'] == False:
            try:
                del reaction[reaction.index(message.author.id)]
            except ValueError:
                pass

        if len(reaction) > config['starboard']['threshold']:
            data = {'_id': payload.message_id, 'channel': payload.channel_id, 'guild': payload.guild_id, 'author': message.author.id, 'message': message.content}
            starboard_channel = self.bot.get_channel(config['starboard']['channel'])
            if not starboard_channel:
                return

            already_starred = await self.bot.starboard.find(message.id)
            if already_starred:
                self.bot.temp_star.append(message.id)
                try:
                    starboard_message = await starboard_channel.fetch_message(already_starred['starboard_message'])
                except discord.NotFound:
                    await self.bot.starboard.delete(message.id)
                
                await starboard_message.edit(content=f"{message.channel.mention} | ⭐ {len(reaction)}")
                self.bot.temp_star.remove(message.id)
                return

            try:
                
                self.bot.temp_star.append(message.id)
                embed = discord.Embed()
                embed.color = discord.Color.random()
                if message.content:
                    embed.description = message.content
                embed.set_author(name=message.author.name, icon_url=message.author.avatar.url if message.author.avatar else message.author.default_avatar.url)
                embed.set_footer(text=f"Message ID: {message.id}")
                embed.timestamp = message.created_at
                
                if message.reference:
                    reference = await message.channel.fetch_message(message.reference.message_id)
                    if reference.content:
                        embed.add_field(name="Reply", value=reference.content)
                extra = []
                if len(message.embeds) > 0:
                    for membed in message.embeds:
                        extra.append(membed)
                
                view = discord.ui.View()
                view.add_item(discord.ui.Button(label="View Message", url=message.jump_url, style=discord.ButtonStyle.url))
                extra.append(embed)

                if message.attachments:
                    iembed = discord.Embed()
                    iembed.set_image(url=message.attachments[0].url)
                    extra.append(iembed)
                
                starboard_message = await starboard_channel.send(content=f"{message.channel.mention} | ⭐ {len(reaction)}",embeds=extra, view=view)
                data['starboard_message'] = starboard_message.id
                await self.bot.starboard.insert(data)
                self.bot.temp_star.remove(message.id)
            except Exception as e:
                print(e)
        
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if not payload.guild_id:
            return
        if payload.message_id in self.bot.temp_star:
            return        
        config = await self.bot.config.find(payload.guild_id)
        if not config:
            return
        if config['starboard']['toggle'] == False:
            return
        if payload.channel_id == config['starboard']['channel']:
            return
        try:
            channel = self.bot.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
        except discord.NotFound:
            return
        
        reaction = []
        for reactions in message.reactions:
            if reactions.emoji == "⭐":
                reaction = [user.id async for user in reactions.users()]
                break
        if len (reaction) == 0:
            return

        if config['starboard']['self_star'] == True:
            pass
        elif config['starboard']['self_star'] == False:
            try:
                del reaction[reaction.index(message.author.id)]
            except ValueError:
                pass
        
        if len(reaction) > config['starboard']['threshold']:
            data = {'_id': payload.message_id, 'channel': payload.channel_id, 'guild': payload.guild_id, 'author': message.author.id, 'message': message.content}
            starboard_channel = self.bot.get_channel(config['starboard']['channel'])
            if not starboard_channel:
                return

            already_starred = await self.bot.starboard.find(message.id)
            if already_starred:
                self.bot.temp_star.append(message.id)
                try:
                    starboard_message = await starboard_channel.fetch_message(already_starred['starboard_message'])
                except discord.NotFound:
                    await self.bot.starboard.delete(message.id)
                
                await starboard_message.edit(content=f"{message.channel.mention} | ⭐ {len(reaction)}")
                self.bot.temp_star.remove(message.id)    


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

class Commands_Checks(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Loaded {self.__class__.__name__}")
    
    @app_commands.command(nae="toggle", description="Toggle starboard on/off")
    @app_commands.describe(toggle="True/False")
    @app_commands.default_permissions(manage_guild=True)
    async def toggle(self, interaction: discord.Interaction, toggle: bool=True):
        guild_data = await self.bot.config.find(interaction.guild.id)
        guild_data['starboard']['toggle'] = toggle
        await self.bot.config.update(interaction.guild.id, guild_data)
        embed = discord.Embed(title="Starboard Toggle", description=f"Starboard toggle set to {'<:Toggle_on:1029771260114243584>' if toggle else '<:Toggle_off:1029770614430498926>'}", color=0x9e3bff)
        await interaction.response.send_message(embed=embed, ephemeral=False)
    
    @app_commands.command(name="channel", description="Set starboard channel")
    @app_commands.describe(channel="Channel")
    @app_commands.default_permissions(manage_guild=True)
    async def channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        guild_data = await self.bot.config.find(interaction.guild.id)
        guild_data['starboard']['channel'] = channel.id
        await self.bot.config.update(interaction.guild.id, guild_data)
        embed = discord.Embed(title="Starboard Channel", description=f"Starboard channel set to {channel.mention}", color=0x9e3bff)
        await interaction.response.send_message(embed=embed, ephemeral=False)
    
    @app_commands.command(nae="threshold", description="Set starboard threshold")
    @app_commands.describe(threshold="Threshold")
    @app_commands.default_permissions(manage_guild=True)
    async def threshold(self, interaction: discord.Interaction, threshold: app_commands.Range[int, 3, 20]=5):
        guild_data = await self.bot.config.find(interaction.guild.id)
        guild_data['starboard']['threshold'] = threshold
        await self.bot.config.update(interaction.guild.id, guild_data)
        embed = discord.Embed(title="Starboard Threshold", description=f"Starboard threshold set to {threshold}", color=0x9e3bff)
        await interaction.response.send_message(embed=embed, ephemeral=False)
    
    @app_commands.command(nae="selfstar", description="Toggle starboard self star")
    @app_commands.describe(toggle="True/False")
    @app_commands.default_permissions(manage_guild=True)
    async def selfstar(self, interaction: discord.Interaction, toggle: bool=False):
        guild_data = await self.bot.config.find(interaction.guild.id)
        guild_data['starboard']['self_star'] = toggle
        await self.bot.config.update(interaction.guild.id, guild_data)
        embed = discord.Embed(title="Starboard Self Star", description=f"Starboard self star set to {'<:Toggle_on:1029771260114243584>' if toggle else '<:Toggle_off:1029770614430498926>'}", color=0x9e3bff)
        await interaction.response.send_message(embed=embed, ephemeral=False)
    
    @app_commands.command(nae="info", description="Get starboard info")
    @app_commands.default_permissions(manage_guild=True)
    async def info(self, interaction: discord.Interaction):
        guild_data = await self.bot.config.find(interaction.guild.id)
        embed = discord.Embed(title="Starboard Info", description=f"Starboard toggle: {'<:Toggle_on:1029771260114243584>' if guild_data['starboard']['toggle'] else '<:Toggle_off:1029770614430498926>'}\nStarboard channel: {interaction.guild.get_channel(guild_data['starboard']['channel'])}\nStarboard threshold: {guild_data['starboard']['threshold']}\nStarboard self star: {'<:Toggle_on:1029771260114243584>' if guild_data['starboard']['self_star'] else '<:Toggle_off:1029770614430498926>'}", color=0x9e3bff)
        await interaction.response.send_message(embed=embed, ephemeral=False)

async def setup(bot):
    await bot.add_cog(Starboard(bot))

            # await self.bot.starboard.insert({
            #     '_id': message.id,
            #     'guildId': guild.id,
            #     'authorId': message.author.id,
            #     'channelId': channel.id,
            #     'starboard_message_id': starborad_sent_message.id,
            # })
from discord import app_commands
from discord.ext import commands
from paginator import Paginator
from bson.objectid import ObjectId
import discord
import datetime

class Warn(commands.Cog, name="Warning System", description="Server Warning logging"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @commands.hybrid_command(name="warn", description="Warn a user", brife="warning <user> <reason>")
    @app_commands.describe(user="The user to warn", reason="The reason for the warning")
    @app_commands.guilds(964377652813234206)
    async def warn(self, ctx , user: discord.Member, *, reason:str):
        warn_data = {"user":user.id, "reason":reason, "mod":ctx.author.id, 'time': datetime.datetime.utcnow(), "guild":ctx.guild.id}
        guild_data = await self.bot.config.find(ctx.guild.id)
        print(guild_data)
        if not ctx.interaction:
            await ctx.message.delete()
        await self.bot.warns.insert(warn_data)
        try:
            await user.send(f"You have been warned in {ctx.guild.name} for {reason}")
        except discord.HTTPException:
            pass
        embed = discord.Embed(description=f"<:allow:819194696874197004> | {user.mention} has been warned", color=0x32CD32)
        await ctx.send(embed=embed)

        log_embed = discord.Embed(title=f":warning: Warning | Case ID: {guild_data['case']}", color=0xFF0000)
        log_embed.description = f"Offender: {user.display_name} | {user.mention}\nReason: {reason}\nModerator: {ctx.author.display_name} | {ctx.author.mention}"
        log_embed.set_footer(text=f"ID: {user.id}")
        log_embed.timestamp = datetime.datetime.utcnow()

        log_channel = self.bot.get_channel(guild_data['mod_log'])
        await log_channel.send(embed=log_embed)
        await self.bot.config.increment(ctx.guild.id, 1,'case')

    @app_commands.command(name="warnings", description="Get a user's warnings")
    @app_commands.describe(user="The user to get warnings for")
    @app_commands.guilds(964377652813234206)
    async def warnings(self, interaction: discord.Interaction, user: discord.Member):
        warns = await self.bot.warns.find_many_by_custom({'user':user.id, 'guild':interaction.guild.id})
        
        if warns:
            pages = []
            for warn in warns:
                embed = discord.Embed(title=f"{user.name}'s Warnings", description=f"ID: {warn['_id']}\nReason: {warn['reason']}\nModerator: {self.bot.get_user(warn['mod']).mention}\nTime: <t:{round(warn['time'].timestamp())}:R>", color=0x32CD32)
                pages.append(embed)
            
            await Paginator(interaction, pages).start(embeded=True, quick_navigation=False)
        else:
            await interaction.response.send_message("<:deny:819194696874197004> | This user has no warnings", ephemeral=True)
        
    
    @app_commands.command(name="clearwarn", description="Clear a user's warnings")
    @app_commands.describe(user="The user to clear warnings for")
    @app_commands.guilds(964377652813234206)
    async def clearwarn(self, interaction: discord.Interaction, user: discord.Member, reason:str):
        warns = await self.bot.warns.find_many_by_custom({'user':user.id, 'guild':interaction.guild.id})
        guild_data = await self.bot.config.find(interaction.guild.id)
        if warns:
            for warn in warns:
                await self.bot.warns.delete(warn['_id'])
            await interaction.response.send_message("<:allow:819194696874197004> | Warnings cleared", ephemeral=True)

            log_embed = discord.Embed(title=f":warning: Warning Clears | Case ID: {guild_data['case']}", color=0x32CD32)
            log_embed.description = f"Offender: {user.display_name} | {user.mention}\nReason: {reason}\nModerator: {interaction.user.display_name} | {interaction.user.mention}"
            log_embed.set_footer(text=f"ID: {user.id}")
            log_embed.timestamp = datetime.datetime.utcnow()

            log_channel = self.bot.get_channel(guild_data['mod_log'])
            await log_channel.send(embed=log_embed)
            await self.bot.config.increment(interaction.guild.id, 1,'case')

        else:
            await interaction.response.send_message("<:deny:819194696874197004> | This user has no warnings", ephemeral=True)
        


    
    @app_commands.command(name="delwarn", description="Delete a warning")
    @app_commands.describe(warn="The warning ID to delete")
    @app_commands.guilds(964377652813234206)
    async def delwarn(self, interaction: discord.Interaction, warn: str):
        warn_id = ObjectId(warn)
        warn = await self.bot.warns.find({"_id":warn_id})
        if warn:
            await self.bot.warns.delete({"_id":warn_id})
            await interaction.response.send_message(f"<:allow:819194696874197004> | Warning deleted with ID: {warn['_id']}", ephemeral=True)

            guild_data = await self.bot.config.find({"_id":interaction.guild.id})
            log_embed = discord.Embed(title=f":warning: Warning Deleted | Case ID: {guild_data['case']}", color=0x32CD32)
            log_embed.description = f"Offender: {self.bot.get_user(warn['user']).display_name} | {self.bot.get_user(warn['user']).mention}\nReason: {warn['reason']}\nModerator: {interaction.user.display_name} | {interaction.user.mention}"
            log_embed.set_footer(text=f"ID: {warn['user']}")
            log_embed.timestamp = datetime.datetime.utcnow()

            log_channel = self.bot.get_channel(guild_data['mod_log'])
            await log_channel.send(embed=log_embed)
            await self.bot.config.increment(interaction.guild.id, 1,'case')

        else:
            await interaction.response.send_message("<:deny:819194696874197004> | This warning does not exist", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Warn(bot))
    

import discord
from discord.ext import commands
from discord import app_commands
from copy import deepcopy
from utils.checks import Commands_Checks, Dynamic_cooldown
class AFK(commands.Cog, name="AFK", description="Member Afk Module"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        if message.guild.id != 785839283847954433: return
        current_afk = deepcopy(self.bot.current_afk)

        if message.author.id in self.bot.current_afk:
            value  = self.bot.current_afk[message.author.id]
            try:
                await message.author.edit(nick=value['last_name'])
            except:
                pass            
            

            embed = discord.Embed(description=f"{message.author.mention} is no longer AFK\nAFK Started: <t:{value['time']}:R> ago", color=0x00ff00)

            await message.reply(embed=embed)
            await self.bot.afk.delete(message.author.id)

            try:
                self.bot.current_afk.pop(message.author.id)
            except KeyError:
                pass
            return
        
        if message.reference:
            try:
                reply_message = await message.channel.fetch_message(message.reference.message_id)
            except discord.NotFound:
                return
            for key, value in current_afk.items():
                if reply_message.author.id == key:
                    user = message.guild.get_member(key)
                    embed = discord.Embed(description=f"Reason: {value['message']}\nAFK Started: <t:{value['time']}:R>", color=user.color)
                    embed.set_author(name=f"{user.display_name} is AFK", icon_url=user.avatar.url if user.avatar else user.default_avatar)
                    return await message.reply(embed=embed)

        if len(message.mentions) > 0:
            for key, value in current_afk.items():
                if key in [_id.id for _id in message.mentions]:
                    user = message.guild.get_member(key)
                    embed = discord.Embed(description=f"Reason: {value['message']}\nAFK Started: <t:{value['time']}:R>", color=user.color)
                    embed.set_author(name=f"{user.display_name} is AFK", icon_url=user.avatar.url if user.avatar else user.default_avatar)
                    return await message.reply(embed=embed)

    @app_commands.command(name="afk", description="Set your AFK status")
    @app_commands.guilds(785839283847954433)
    @app_commands.describe(status="Your AFK reason")
    @app_commands.checks.dynamic_cooldown(Dynamic_cooldown.is_me)
    async def afk(self, interaction: discord.Interaction, status: str = None):
        afk_data = await self.bot.afk.find(interaction.user.id)
        if afk_data:
            await interaction.response.send_message("You are already afk", ephemeral=True)
            return

        afk_data = {'_id':interaction.user.id, 'message': status, 'last_name': interaction.user.display_name,'time': round(discord.utils.utcnow().timestamp())}
        await self.bot.afk.insert(afk_data)
        embed = discord.Embed(description=f"{interaction.user.mention} You are now afk\nReason: {status}", color=0x00ff00)
        embed.set_author(name=f"{interaction.user.display_name} is now afk", icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar)

        await interaction.response.send_message(embed=embed)
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
    await bot.add_cog(AFK(bot))
    


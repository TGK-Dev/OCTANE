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
        if message.author.bot or message.guild is None:
            return
        
        if message.guild.id != 785839283847954433: return
        if message.author.id in self.bot.current_afk.keys():
            try:
                await message.author.edit(nick=self.bot.current_afk[message.author.id]['last_name'])
            except discord.Forbidden:
                pass
            await message.reply("Welcome back! I have removed your AFK status.")            
            await self.bot.afk.delete(message.author.id)
            del self.bot.current_afk[message.author.id]
        
        if len(message.mentions) > 0:
            for user in message.mentions:
                if user.id in self.bot.current_afk.keys():
                    afk = self.bot.current_afk[user.id]
                    await message.reply(f"{user.mention} is AFK Since <t:{afk['time']}:R>\nReason: {afk['message']}", delete_after=10, allowed_mentions=discord.AllowedMentions(users=False, roles=False, everyone=False))
        
        if message.interaction != None:
            interaction = message.interaction
            if interaction.user.id in self.bot.current_afk.keys():
                try:
                    await interaction.user.edit(nick=self.bot.current_afk[interaction.user.id]['last_name'])
                except discord.Forbidden:
                    pass
                await message.reply("Welcome back! I have removed your AFK status.")
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

        afk_data = {'_id':interaction.user.id, 'message': status, 'last_name': interaction.user.display_name,'time': round(discord.utils.utcnow().timestamp())}
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
    await bot.add_cog(AFK(bot))
    


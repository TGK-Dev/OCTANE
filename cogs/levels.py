import discord 
from discord import app_commands
from discord.ext import commands
from amari import AmariClient
import asyncio
import aiohttp
class ButtonOnCooldown(commands.CommandError):
  def __init__(self, retry_after: float):
    self.retry_after = retry_after

def key(interaction: discord.Interaction):
  return interaction.user
class level_check(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)
        self.cd = commands.CooldownMapping.from_cooldown(1.0, 300, key)    
    
    async def interaction_check(self, interaction: discord.Interaction):
        retry_after = self.cd.update_rate_limit(interaction)
        if retry_after:
            raise ButtonOnCooldown(retry_after)
        
        return True
    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item):
        if isinstance(error, ButtonOnCooldown):
            seconds = int(error.retry_after)
            unit = 'second' if seconds == 1 else 'seconds'
            await interaction.response.send_message(f"You're on cooldown for {seconds} {unit}!", ephemeral=True)
        else:
            await super().on_error(interaction, error, item)

    @discord.ui.button(label='Check Level', style=discord.ButtonStyle.green, custom_id="LEVEL:CHECK")
    async def count(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Getting data...", ephemeral=True)
        data = await self.bot.Amari_api.fetch_user(interaction.guild.id, interaction.user.id)
        embed = discord.Embed(description=f"**Name:** {interaction.user.mention}\n**Level:** {data.level}\n**XP:** {data.exp}\n**Weeklyexp:** {data.weeklyexp}", color=interaction.user.color)
        embed.timestamp = discord.utils.utcnow()
        embed.set_footer(text=f"{interaction.user.name}#{interaction.user.discriminator}", icon_url=self.bot.user.avatar.url)
        await interaction.edit_original_response(content=None, embed=embed)


class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession()
        self.bot.Amari_api = AmariClient(bot.Amari_token)
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(level_check(self.bot))
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @app_commands.command(name="level")
    @app_commands.default_permissions(administrator=True)
    @app_commands.guilds(785839283847954433, 811037093715116072)
    async def level(self, interaction: discord.Interaction):
        embed = discord.Embed(description="Click Below Button To Check Level", color=0xADD8E6)
        await interaction.response.send_message(embed=embed, view=level_check(self.bot))
    
    @app_commands.command(name="startcard", description="Start giving cards to users")
    @app_commands.default_permissions(administrator=True)
    @app_commands.guilds(785839283847954433)
    async def startcard(self, interaction: discord.Interaction):
        lb_data = await self.bot.Amari_api.fetch_full_leaderboard(interaction.guild.id, weekly=True)
        level1 = interaction.guild.get_role(1012753458065051772)
        level2 = interaction.guild.get_role(1012753498628173925)
        level3 = interaction.guild.get_role(1012753537878478969)
        await interaction.response.send_message("Starting card giving...")
        async with interaction.channel.typing():
            for user in lb_data:
                member = interaction.guild.get_member(user.user_id)
                if user.exp >= 10:
                    await member.add_roles(level1)
                if user.exp >= 50:
                    await member.add_roles(level2)
                if user.exp >= 100:
                    await member.add_roles(level3)
                await asyncio.sleep(2)
        await interaction.edit_original_response(content="Done!")
        
async def setup(bot):
    await bot.add_cog(Levels(bot))
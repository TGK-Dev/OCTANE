import discord
from discord import Interaction
from discord.ext import commands
import os
import asyncio

class select(discord.ui.Select):
    def __init__(self, bot, ctx):
        self.bot = bot
        self.ctx = ctx
    
        options  = []
        for ext in os.listdir("./cogs/"):
            if ext.endswith(".py") and not ext.startswith("_"):
                options.append(discord.SelectOption(label=f"cogs.{ext[:-3]}", value=f"cogs.{ext[:-3]}"))
        
        options.append(discord.SelectOption(label="Relaod All", value="all"))
        
    
        super().__init__(placeholder='Select Cog from Below', options=options, max_values=len(options), min_values=1)
    

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)

        if "all" not in self.values:

            embed = discord.Embed(
                    title="Reloading all cogs!",
                    color=0x808080,
                    timestamp=self.ctx.message.created_at
                )

            for value in self.values:
                if value == "all":
                    continue
                try:
                    await self.bot.unload_extension(value)
                    await self.bot.load_extension(value)
                    embed.add_field(
                        name=f"Reloaded: `{value}`",
                        value='\uFEFF',
                        inline=False
                    )
                except Exception as e:
                    embed.add_field(
                        name=f"Failed to reload: `{value}`",
                        value=f"```\n{e}\n```",
                        inline=False
                    )
                await asyncio.sleep(0.5)
            await interaction.followup.send(embed=embed)

        else:
            embed = discord.Embed(
                    title="Reloading all cogs!",
                    color=0x808080,
                    timestamp=self.ctx.message.created_at
                )
            
            for ext in os.listdir("./cogs/"):
                    if ext.endswith(".py") and not ext.startswith("_"):
                        try:
                            await self.bot.unload_extension(f"cogs.{ext[:-3]}")
                            await self.bot.load_extension(f"cogs.{ext[:-3]}")
                            embed.add_field(
                                name=f"Reloaded: `{ext}`",
                                value='\uFEFF',
                                inline=False
                            )
                        except Exception as e:
                            embed.add_field(
                                name=f"Failed to reload: `{ext}`",
                                value=e,
                                inline=False
                            )
                        await asyncio.sleep(0.5)
            
            await interaction.followup.send(embed=embed)

class Cog_select(discord.ui.View):
    def __init__(self, bot, ctx):
        super().__init__(timeout=10)
        self.bot = bot
        self.ctx = ctx
    
        self.add_item(select(self.bot, self.ctx))

    async def interaction_check(self, interaction: Interaction):
        if interaction.user.id in self.bot.owner_ids:
            return True
        else:
            return False
    

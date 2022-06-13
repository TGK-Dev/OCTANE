from discord.ext import commands
import discord

class Suggestion(commands.Cog, name="Suggestion", description="Suggestion Module"):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @commands.command(name="Suggestion", aliases=["suggest"], description="Suggestion Command", brief="Suggest <suggestion>")

    async def suggest(self, ctx, *, suggestion):
        guild_data = await self.bot.config.find(ctx.guild.id)
        if not guild_data["suggestion_channel"]:
            await ctx.send("Suggestion channel not set")
            return
        suggestion_count = len(await self.bot.suggestions.get_all()) + 1
        suggestion_embed = discord.Embed(title=f"Suggestion #{suggestion_count}", description=suggestion, color=0x00ff00)
        suggestion_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)

        message = await self.bot.get_channel(guild_data["suggestion_channel"]).send(embed=suggestion_embed)

        suggestion_data = {"_id": suggestion_count, "author": ctx.author.id,"message_id": message.id}
        await self.bot.suggestions.insert(suggestion_data)

        await message.add_reaction("⬆️")
        await message.add_reaction("⬇️")

        await ctx.send(f"Suggestion #{suggestion_count} has been submitted")
        await ctx.message.delete()

    @commands.command(name="Accept", aliases=['approve', 'ap'], description="Mark Suggestion as Accepted", brief="Accept <suggestion number>")
    
    async def accept(self, ctx, suggestion_number: int, *, reason: str = "No reason provided"):
        suggestion_data = await self.bot.suggestions.find(suggestion_number)
        if not suggestion_data:
            await ctx.send("Enter a valid suggestion number")
        if suggestion_data:
            if suggestion_data['author'] == ctx.author.id:
                return await ctx.send("You can't accept your own suggestion")
            
            guild_data = await self.bot.config.find(ctx.guild.id)
            if not guild_data["suggestion_channel"]:
                await ctx.send("Suggestion channel not set")
                return
            
            suggestion_channel = self.bot.get_channel(guild_data["suggestion_channel"])
            suggestion_message = await suggestion_channel.fetch_message(suggestion_data["message_id"])
            suggestion_embed = suggestion_message.embeds[0]
            suggestion_embed.clear_fields()
            suggestion_embed.title = f"Suggestion #{suggestion_number} - Accepted"
            suggestion_embed.color = 0x00ff00
            suggestion_embed.add_field(name="Reason", value=reason)
            await suggestion_message.edit(embed=suggestion_embed)
            await suggestion_message.clear_reactions()
            await suggestion_message.add_reaction("✅")
            await ctx.send(f"Suggestion #{suggestion_number} has been accepted")
            dm_embed = discord.Embed(title=f"Suggestion #{suggestion_number} - Accepted", description=f"your suggestion has been accepted by {ctx.author.mention}", color=0x00ff00)
            dm_embed.add_field(name="Reason", value=reason)
            try:
                await ctx.author.send(embed=dm_embed)
            except discord.HTTPException:
                pass
    
    @commands.command(name="Reject", description="Mark Suggestion As Rejected", brief="Reject <suggestion number>")
    async def reject(self, ctx, suggestion_number: int, *, reason: str = "No reason provided"):
        suggestion_data = await self.bot.suggestions.find(suggestion_number)
        if not suggestion_data:
            await ctx.send("Enter a valid suggestion number")
        if suggestion_data:
            if suggestion_data['author'] == ctx.author.id:
                return await ctx.send("You can't reject your own suggestion")
            
            guild_data = await self.bot.config.find(ctx.guild.id)
            if not guild_data["suggestion_channel"]:
                await ctx.send("Suggestion channel not set")
                return
            
            suggestion_channel = self.bot.get_channel(guild_data["suggestion_channel"])
            suggestion_message = await suggestion_channel.fetch_message(suggestion_data["message_id"])
            suggestion_embed = suggestion_message.embeds[0]
            suggestion_embed.clear_fields()
            suggestion_embed.title = f"Suggestion #{suggestion_number} - Rejected"
            suggestion_embed.color = 0xff0000
            suggestion_embed.add_field(name="Reason", value=reason)
            await suggestion_message.edit(embed=suggestion_embed)
            await suggestion_message.clear_reactions()
            await suggestion_message.add_reaction("❌")
            await ctx.send(f"Suggestion #{suggestion_number} has been rejected")
            dm_embed = discord.Embed(title=f"Suggestion #{suggestion_number} - Rejected", description=f"your suggestion has been rejected by {ctx.author.mention}", color=0xff0000)
            dm_embed.add_field(name="Reason", value=reason)
            try:
                await ctx.author.send(embed=dm_embed)
            except discord.HTTPException:
                pass
    
    @commands.command(name="Delete", description="Delete Suggestion from Database and Channel", brief="Delete <suggestion number>")
    async def delete(self, ctx, suggestion_number: int):
        suggestion_data = await self.bot.suggestions.find(suggestion_number)
        if not suggestion_data:
            await ctx.send("Enter a valid suggestion number")
        if suggestion_data:
            if suggestion_data['author'] == ctx.author.id:
                return await ctx.send("You can't delete your own suggestion")
            
            guild_data = await self.bot.config.find(ctx.guild.id)
            if not guild_data["suggestion_channel"]:
                await ctx.send("Suggestion channel not set")
                return
            
            suggestion_channel = self.bot.get_channel(guild_data["suggestion_channel"])
            suggestion_message = await suggestion_channel.fetch_message(suggestion_data["message_id"])
            await suggestion_message.delete()
            await self.bot.suggestions.delete(suggestion_number)
            await ctx.send(f"Suggestion #{suggestion_number} has been deleted")   
    
    @commands.command(name="Consider",description="Mark Suggestion As Considered ", brief="Consider <suggestion number>")
    async def considered(self, ctx, suggestion_number: int, ):
        suggestion_data = await self.bot.suggestions.find(suggestion_number)
        if not suggestion_data:
            await ctx.send("Enter a valid suggestion number")
        if suggestion_data:
            if suggestion_data['author'] == ctx.author.id:
                return await ctx.send("You can't consider your own suggestion")
            
            guild_data = await self.bot.config.find(ctx.guild.id)
            if not guild_data["suggestion_channel"]:
                await ctx.send("Suggestion channel not set")
                return
            
            suggestion_channel = self.bot.get_channel(guild_data["suggestion_channel"])
            suggestion_message = await suggestion_channel.fetch_message(suggestion_data["message_id"])
            suggestion_embed = suggestion_message.embeds[0]
            suggestion_embed.clear_fields()
            suggestion_embed.title = f"Suggestion #{suggestion_number} - Considered"
            suggestion_embed.color = 0x00ff00
            await suggestion_message.edit(embed=suggestion_embed)
            await suggestion_message.clear_reactions()
            await suggestion_message.add_reaction("🔄")
            await ctx.send(f"Suggestion #{suggestion_number} has been considered")
            dm_embed = discord.Embed(title=f"Suggestion #{suggestion_number} - Considered", description=f"your suggestion has been considered by {ctx.author.mention}", color=0x00ff00)
            try:
                await ctx.author.send(embed=dm_embed)
            except discord.HTTPException:
                pass         
    
    @commands.command(name="Implement", description="Mark Suggestion As Implemented", brief="Implement <suggestion number>")
    async def implemented(self, ctx, suggestion_number: int, *, reason: str = "No reason provided"):
        suggestion_data = await self.bot.suggestions.find(suggestion_number)
        if not suggestion_data:
            await ctx.send("Enter a valid suggestion number")
        if suggestion_data:
            if suggestion_data['author'] == ctx.author.id:
                return await ctx.send("You can't implement your own suggestion")
            
            guild_data = await self.bot.config.find(ctx.guild.id)
            if not guild_data["suggestion_channel"]:
                await ctx.send("Suggestion channel not set")
                return
            
            suggestion_channel = self.bot.get_channel(guild_data["suggestion_channel"])
            suggestion_message = await suggestion_channel.fetch_message(suggestion_data["message_id"])
            suggestion_embed = suggestion_message.embeds[0]
            suggestion_embed.clear_fields()
            suggestion_embed.title = f"Suggestion #{suggestion_number} - Implemented"
            suggestion_embed.color = 0x00ff00
            await suggestion_message.edit(embed=suggestion_embed)
            await suggestion_message.clear_reactions()
            await suggestion_message.add_reaction("✅")
            await ctx.send(f"Suggestion #{suggestion_number} has been implemented")

            dm_embed = discord.Embed(title=f"Suggestion #{suggestion_number} - Implemented", description=f"your suggestion has been implemented by {ctx.author.mention}", color=0x00ff00)
            dm_embed.add_field(name="Reason", value=reason)
            try:
                await ctx.author.send(embed=dm_embed)
            except discord.HTTPException:
                pass
            

async def setup(bot):
    await bot.add_cog(Suggestion(bot))
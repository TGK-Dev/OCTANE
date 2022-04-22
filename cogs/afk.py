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
        current_afk = deepcopy(self.bot.current_afk)

        if message.author.id in self.bot.current_afk:

            try:
                self.bot.current_afk.pop(message.author.id)
            except KeyError:
                pass

            try:
                await message.author.edit(nick=self.bot.current_afk[message.author.id]['last_name'])
            except:
                pass

            await message.reply(f"{message.author.mention} Your AFK status has been removed.")
            await self.bot.afk.delete(message.author.id)
            return
        
        if message.reference:
            reply_message = await message.channel.fetch_message(message.reference.message_id)
            for key, value in current_afk.items():
                if reply_message.author.id == key:
                    user = message.guild.get_member(key)
                    return await message.reply(f"{user.display_name} is afk {value['message']} -<t:{value['time']}:R> <t:{value['time']}:f>", mention_author=False, delete_after=30, allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))

        if len(message.mentions) > 0:
            for key, value in current_afk.items():
                if key in [_id.id for _id in message.mentions]:
                    user = message.guild.get_member(key)
                    return await message.reply(f"{user.display_name} is afk {value['message']} -<t:{value['time']}:R> <t:{value['time']}:f>", mention_author=False, delete_after=30, allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))        

    @commands.hybrid_command(name="afk", description="Set your AFK status", brief="afk [status]")
    @app_commands.guilds(785839283847954433)
    @app_commands.describe(status="Your AFK reason")
    @app_commands.checks.dynamic_cooldown(Dynamic_cooldown.is_me)
    @commands.check_any(Commands_Checks.is_me(), Commands_Checks.is_owner(), Commands_Checks.can_use())
    async def afk(self, ctx, status: str = None):
        afk_data = await self.bot.afk.find(ctx.author.id)
        if afk_data:
            await ctx.send("You are already afk", ephemeral=True)
            return

        afk_data = {'_id': ctx.author.id, 'message': status, 'last_name': ctx.author.display_name,'time': round(discord.utils.utcnow().timestamp())}
        await self.bot.afk.insert(afk_data)
        await ctx.send("You are now afk", ephemeral=True)
        try:
            await ctx.author.edit(nick=f"{ctx.author.display_name} AFK")
        except:
            pass
        
        self.bot.current_afk[ctx.author.id] = afk_data
    
async def setup(bot):
    await bot.add_cog(AFK(bot))
    


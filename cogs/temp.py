import discord
from discord.ext import commands
from io import BytesIO
import random
class Temp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Temp is ready.')

    @commands.command()
    async def get_logs(self, ctx, guild: discord.Guild):
        msg = await ctx.send("Getting logs...")
        #bot_added = [log async for log in guild.audit_logs(limit=None, action=discord.AuditLogAction.bot_add)]

        #role_update = [log async for log in guild.audit_logs(limit=None, action=discord.AuditLogAction.role_update)]
        meber_update = [log async for log in guild.audit_logs(limit=None, action=discord.AuditLogAction.member_role_update)]
        data = ""
        await msg.edit(content="Got logs")
        for logs in meber_update:
            num = random.randint(0, 10)
            new_roles = list(set(logs.after.roles).difference(set(logs.before.roles)))
            data += f"{logs.user.name}({logs.user.id}) {logs.action} {logs.target.name} roles from {new_roles}\n"

        #create file
        buffer = BytesIO(data.encode('utf-8'))
        file = discord.File(buffer, filename=f"{guild.name}-{guild.id}-member-role-update.txt")
        buffer.close()
        await msg.edit(content=None, attachments=[file])
        
    @commands.command()
    async def leave(self, ctx):
        await ctx.send("Leaving...")
        await ctx.guild.leave()

        

    
async def setup(bot):
    await bot.add_cog(Temp(bot))
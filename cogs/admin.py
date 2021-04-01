import discord
from datetime import datetime
from discord.ext import commands


class Admins(commands.Cog):
	"""docstring for Example"""
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_ready(self):
		print(f"{self.__class__.__name__} Cog has been loaded\n-----")

	@commands.command(name="activity", description="Change Bot activity", usage="[activity]")
	@commands.has_permissions(administrator=True)
	async def activity(self, ctx, *, activity):
		
		await self.bot.change_presence(activity=discord.Game(name=f"{activity}")) # This changes the bots 'activity'
		await ctx.send('Bot activity is Updated')
	
	@commands.command(name="Status", description="Change Bot Status to online & Dnd & idle", usage="[dnd & idle & online]")
	@commands.has_permissions(administrator=True)
	async def status(self,ctx, arg):
		if arg == 'dnd':
			await self.bot.change_presence(status=discord.Status.dnd)
			await ctx.send('Bot status is Updated')
		elif arg == 'online':
			await self.bot.change_presence(status=discord.Status.online)
			await ctx.send('Bot status is Updated')
		elif arg == 'idle' :
			await self.bot.change_presence(status=discord.Status.idle)
			await ctx.send('Bot status is Updated')
		else: 
			await ctx.send(f'{ctx.author.mention} Plsease Provide The vaild Status')
			await ctx.send('Bot status is Updated')

	@commands.command(name="Say", description="And classic say command", usage="[anything]")
	@commands.has_permissions(administrator=True)
	async def say(self,ctx, *, say):
		await ctx.message.delete()
		await ctx.send(f'{say}')

	@commands.command(name="toggle", description="Enable or disable a command!")
    @commands.has_role(785842380565774368)
    async def toggle(self, ctx, *, command):
        command = self.bot.get_command(command)

        if command is None:
            await ctx.send("I can't find a command with that name!")

        elif ctx.command == command:
            await ctx.send("You cannot disable this command.")

        else:
            command.enabled = not command.enabled
            ternary = "enabled" if command.enabled else "disabled"
            await ctx.send(f"I have {ternary} {command.qualified_name} for you!")


def setup(bot):
	bot.add_cog(Admins(bot))
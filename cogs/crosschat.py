from discord.ext import commands
from discord import app_commands, Embed
import discord

class CorssChat(commands.Cog, name="Cross Chat"):
    def __init__(self, bot):
        self.bot = bot

    async def Send_web_Message(self, channel: discord.TextChannel, message: discord.Message) -> discord.Message:
        webhook = None
        for webhook in await channel.webhooks():
            if webhook.user.id == self.bot.user.id:
                webhook = webhook
                break
        
        if webhook is None:
            webhook = await channel.create_webhook(name="CrossChat",reason="CrossChat")
        if message.author.avatar.url != None:
            avatar = message.author.avatar.url
        else:
            avatar = message.author.default_avatar
        content = message.content
        for attachment in message.attachments:
            content += f"\n{attachment.url}"
        return await webhook.send(content=content, username=message.author.name, avatar_url=avatar, allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")

    
    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.cross_chat_toggle == False:
            return
        
        if message.content.startswith("-"):
            return
            
        if message.author.bot:
            return
        
        if message.author.id in self.bot.blacklist_users:
            return 

        if message.channel.id == 970681327374467082:
            place2 = self.bot.get_channel(970681794242420736)

            send_msg = await self.Send_web_Message(place2, message)
        
        if message.channel.id == 970681794242420736:
            place1 = self.bot.get_channel(970681327374467082)

            send_msg = await self.Send_web_Message(place1, message)

    @commands.command(name="crosschat", description="Toggle CrossChat")
    @commands.has_permissions(administrator=True)
    async def crosschat(self, ctx, toggle: str):
        if toggle.lower() == "on" or toggle.lower() == "true":
            self.bot.cross_chat_toggle = True
            await ctx.send("CrossChat is now on")
        elif toggle.lower() == "off" or toggle.lower() == "false":
            self.bot.cross_chat_toggle = False
            await ctx.send("CrossChat is now off")
        else:
            await ctx.send("Please use `on` or `off` or `true` or `false`")


async def setup(bot):
    await bot.add_cog(CorssChat(bot))

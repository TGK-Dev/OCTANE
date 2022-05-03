from discord.ext import commands
from discord import app_commands, Embed
import discord
import datetime

class CrossChat_slash(app_commands.Group, name="crosschat", description="utils commands for crosschat"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(name='crosschat', description="utils commands for crosschat")
    
    @app_commands.command(name="toggle", description="Turn CrossChat on/off")
    @app_commands.guilds(785839283847954433, 811037093715116072)
    @app_commands.describe(option="select option", reason="reason for turning CrossChat on/off")
    async def toggle(self, interaction: discord.Interaction, option: bool=None, reason: str="No reason provided"):

        if option is None:
            await interaction.response.send_message(f"CrossChat is currently **{self.bot.cross_chat_toggle}**", ephemeral=True)
            return
        else:
            overwrite = discord.PermissionOverwrite()
            overwrite.send_messages = option

            self.bot.cross_chat_toggle = option
            tgk_chat = self.bot.get_channel(970681327374467082)
            await tgk_chat.set_permissions(tgk_chat.guild.default_role, overwrite=overwrite)

            tmm_chat = self.bot.get_channel(970681794242420736)
            await tmm_chat.set_permissions(tmm_chat.guild.default_role, overwrite=overwrite)
            
            if option == True:
                status = "on"
            elif option == False:
                status = "off"
            else:
                status = self.bot.cross_chat_toggle

            embed = Embed(title="CrossChat", description=f"CrossChat is now **{status}**", color=0x2f3136)
            embed.add_field(name="Reason", value=reason)
            embed.set_footer(text=f"{interaction.user.name}#{interaction.user.discriminator}", icon_url=interaction.user.avatar.url)
            embed.timestamp = datetime.datetime.utcnow()

            await tgk_chat.send(embed=embed)
            await tmm_chat.send(embed=embed)
            
            await interaction.response.send_message(f"CrossChat is now **{self.bot.cross_chat_toggle}**", ephemeral=True)
    
    @app_commands.command(name="block", description="Block a user from CrossChat")
    @app_commands.guilds(785839283847954433, 811037093715116072)
    @app_commands.describe(member="select option", reason="reason for blacklisting user")
    async def blacklist(self, interaction: discord.Interaction, member: discord.Member, reason: str="No reason provided"):
        data = await self.bot.crosschat_blacklist.find(member.id)
        if data:
            await interaction.response.send_message(f"{member.mention} is already blacklisted", ephemeral=True)
            return
        else:
            await self.bot.crosschat_blacklist.insert({"_id": member.id, "reason": reason})
            await interaction.response.send_message(f"{member.mention} has been blacklisted", ephemeral=True)

            try:
                self.bot.cross_chat_blacklist.append(member.id)
            except:
                pass

    @app_commands.command(name="unblock", description="Unblock a user from CrossChat")
    @app_commands.guilds(785839283847954433, 811037093715116072)
    @app_commands.describe(member="select option", reason="reason for unblacklisting user")
    async def unblacklist(self, interaction: discord.Interaction, member: discord.Member, reason: str="No reason provided"):
        data = await self.bot.crosschat_blacklist.find(member.id)
        if data:
            await self.bot.crosschat_blacklist.delete(member.id)
            await interaction.response.send_message(f"{member.mention} has been unblacklisted", ephemeral=True)
            
            try:
                self.bot.cross_chat_blacklist.remove(member.id)
            except KeyError:
                pass
        else:
            await interaction.response.send_message(f"{member.mention} is not blacklisted", ephemeral=True)

class CorssChat(commands.Cog, name="Cross Chat"):
    def __init__(self, bot):
        self.bot = bot

    async def Send_web_Message(self, channel: discord.TextChannel, message: discord.Message, reply_message: discord.Message=None) -> discord.Message:
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

        if reply_message is not None:

            if reply_message.author.avatar.url != None:
                embed_avatar = reply_message.author.avatar.url
            else:
                embed_avatar = reply_message.author.default_avatar
            embed = discord.Embed()
            embed.set_author(name=reply_message.author, icon_url=embed_avatar)
            embed.description = reply_message.content
            embed.color = 0xADD8E6
            embed.timestamp = reply_message.created_at
            for attachment in reply_message.attachments:
                embed.set_image(url=attachment.url)
                break
        else:
            embed = None
        return await webhook.send(content=content,embed=embed,username=message.author.display_name, avatar_url=avatar, allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.tree.add_command(CrossChat_slash(self.bot), guild=discord.Object(785839283847954433))
        self.bot.tree.add_command(CrossChat_slash(self.bot), guild=discord.Object(811037093715116072))
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.cross_chat_toggle == False or message.content.startswith("-") or message.author.bot or message.author.id in self.bot.cross_chat_blacklist:
            return

        if message.channel.id == 970681327374467082:
            place2 = self.bot.get_channel(970681794242420736)
            reply_message = None
            if message.reference:
                try:
                    reply_message = await message.channel.fetch_message(message.reference.message_id)
                except discord.NotFound:
                    pass

            send_msg = await self.Send_web_Message(place2, message, reply_message)

        if message.channel.id == 970681794242420736:
            place1 = self.bot.get_channel(970681327374467082)

            reply_message = None
            if message.reference:
                try:
                    reply_message = await message.channel.fetch_message(message.reference.message_id)
                except discord.NotFound:
                    pass

            send_msg = await self.Send_web_Message(place1, message, reply_message)


async def setup(bot):
    await bot.add_cog(CorssChat(bot))

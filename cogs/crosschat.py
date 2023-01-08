from discord.ext import commands, tasks
from discord import app_commands, Embed
from copy import deepcopy
import aiohttp
import discord
import datetime

class CorssChat(commands.GroupCog, name="crosschat", description="utils commands for crosschat"):
    def __init__(self, bot):
        self.bot = bot
        self.cross_chache = {}
    
    @tasks.loop(minutes=2)
    async def cross_chat_loop(self):
        current_messsages = deepcopy(self.cross_chache)
        for key, value in current_messsages.items():
            data = await self.cross_chache[key]
            #check if 30mins have passed from data['time']
            if (datetime.datetime.utcnow() - data['time']).total_seconds() > 1800:
                try:
                    self.cross_chache.pop(key)
                except KeyError:
                    del self.cross_chache[key]
                except Exception as e:
                    pass

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    async def send_crosschat(self, message: discord.Message, other_side: discord.TextChannel, webhook: discord.Webhook):
        embeds = []
        if message.content == None: return        
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(webhook.url, session=session)
            print(message.content)
            await webhook.send(message.content, username=f"{message.author.name}#{message.author.discriminator}", avatar_url=message.author.avatar.url if message.author.avatar else message.author.default_avatar, embeds=embeds, allowed_mentions=discord.AllowedMentions(everyone=False, users=False, roles=False))


    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.cross_chat_toggle == False or message.content.startswith("-") or message.author.bot or message.author.id in self.bot.cross_chat_blacklist:
            return
        if message.author.bot: return
        if not message.guild: return
        if message.author.discriminator == "0000": return
        if message.content is None: return
        other_side = None
        if message.channel.id == 970681327374467082:
            other_side = self.bot.get_channel(972433560327827466)
        elif message.channel.id == 972433560327827466:
            other_side = self.bot.get_channel(970681327374467082)
        else:
            return
        
        if other_side is None:
            return
        else:
            webhook = None
            for webhook in await other_side.webhooks():
                if webhook.user.id == self.bot.user.id:
                    webhook = webhook
                    break
            if webhook is None:
                webhook = await other_side.create_webhook(name="CrossChat", reason="CrossChat webhook")
        
        await self.send_crosschat(message, other_side, webhook)
        
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.id in self.cross_chache.keys():
            other_side_id = self.cross_chache[message.id]['other_side_id']

            other_side_channel_id = self.cross_chache[message.id]['other_side_channel_id']
            other_side_channel = self.bot.get_channel(other_side_channel_id)
            other_side_message = await other_side_channel.fetch_message(other_side_id)
            await other_side_message.delete()
            del self.cross_chache[message.id]
    
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.id in self.cross_chache.keys():
            other_side_data = self.cross_chache[before.id]
            other_side_id = other_side_data['other_side_id']
            other_side_channel = self.bot.get_channel(other_side_data['other_side_channel_id'])

            for webhook in await other_side_channel.webhooks():
                if webhook.user.name == self.bot.user.name:
                    webhook = webhook
                    break
            async with aiohttp.ClientSession() as session:
                url = f"https://canary.discord.com/api/webhooks/{webhook.id}/{webhook.token}"
                webhook = discord.Webhook.from_url(url,session=session)

                await webhook.edit_message(other_side_id, content=after.content)

            
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

            tmm_chat = self.bot.get_channel(972433560327827466)
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


async def setup(bot):
    await bot.add_cog(CorssChat(bot), guilds=[discord.Object(785839283847954433)])

from time import time
import discord
from discord.ext import commands
import re
import requests
import json
import datetime

def is_link_there(str: str):
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex,str)
    if url:
        return [x[0] for x in url]
    else:
        return []

def is_link_bad(link: str):
    url = f"https://bad-domains.walshy.dev/check"
    payload= {"domain": link}
    r = requests.post(url, data=json.dumps(payload)).json()
    return r

class BanButton(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)
        

    @discord.ui.button(label='Ban User', style=discord.ButtonStyle.red, custom_id="BAN:BUTTON")
    async def confirm(self, interaction: discord.Interaction ,button: discord.ui.Button):
        msg = interaction.message.embeds[0].to_dict()
        user = await self.bot.fetch_user(int(msg['footer']['text']))
        if not user:
            return await interaction.response.send_message("User not Found try with command")
        await interaction.guild.ban(user, reason="phishing Links")
        await interaction.response.send_message(f"User {user.name} is Banned")
        
    async def interaction_check(self ,interaction):
        if interaction.user.guild_permissions.ban_members:
            return True
        else:
            await interaction.response.send_message("You don't Have permissions", ephemeral=True)

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invite_regex = re.compile(r"(?:https?://)?(?:www\.)?(?:discord\.(?:gg|io|me|li)|discordapp\.com/invite)/.+[a-z]")
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(BanButton(self.bot))
        print(f'{self.__class__.__name__} Cog has been loaded\n-----')
        self.log_channel = self.bot.get_channel(803687195599962162)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != 935763990670348309: return
        if message.author.bot or message.author.id in self.bot.owner_ids: return
        link_check = re.findall(self.invite_regex, message.content)
        if link_check:
            await message.delete()
            await message.channel.send(f"{message.author.mention} No Invites Allowed", delete_after=10)
            embed = discord.Embed(title="Invite link Tigger", description=f"{message.author.mention} Send invite link in {message.channel.mention}", color=0x00ff00)
            embed.add_field(name="Message", value=message.content, inline=False)
            embed.set_footer(text=f"ID: {message.author.id}")
            embed.timestamp = discord.utils.utcnow()
            await self.log_channel.send(embed=embed)

            if message.author.id not in self.bot.auto_mod_cache:
                self.bot.auto_mod_cache[message.author.id] = {'_id': message.author.id, 'name': message.author.name, 'count': 1, 'last_trigger': datetime.datetime.utcnow()}
            else:
                #check if last_trigger is more than 30min ago
                if (datetime.datetime.utcnow() - self.bot.auto_mod_cache[message.author.id]['last_trigger']).total_seconds() > 1800:
                    self.bot.auto_mod_cache[message.author.id]['count'] = 1
                else:
                    self.bot.auto_mod_cache[message.author.id]['count'] += 1
            
            if self.bot.auto_mod_cache[message.author.id]['count'] >= 3:
                #timeout message author for 30min
                await message.author.timeout(discord.utils.utcnow() + datetime.timedelta(minutes=30), reason="Automod Punishment tirgger")
                #send message to log channel
                embed = discord.Embed(title=f"Muted {message.author.name}",color=0x00ff00)
                embed.add_field(name="Reason", value="Automod Punishment tirgger", inline=False)
                embed.set_footer(text=f"ID: {message.author.id}")
                embed.timestamp = discord.utils.utcnow()
                await self.log_channel.send(embed=embed)
                
        print(self.bot.auto_mod_cache)

    # @commands.Cog.listener()
    # async def on_message(self, message):
        
    #     if self.bot.automod != True: return
    #     if message.author.bot: return
    #     try:
    #         if message.guild.id != 785839283847954433: return
    #     except AttributeError:
    #         return

    #     link = is_link_there(message.content)
    #     if len(message.mentions) >= 9:
    #         if message.author.id in [301657045248114690,488614633670967307,413651113485533194,651711446081601545,810041263452848179,457839031909351425]:
    #             return

    #         await message.delete()
    #         await message.channel.send(f"{message.author.mention} have been warned for mentioning more than 10 people in a message")
    #         await message.author.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(hours=10))

    #     if len(link) > 0:
    #         r = is_link_bad(link[0])
    #         if r['badDomain'] == True:
    #             embed = discord.Embed(description=f"Message Sent by {message.author.mention} Contains known phishing link",color=0xff0000)
    #             embed.add_field(name="Message", value=f"||{message.content}||")
    #             embed.add_field(name="Action Taken", value="Timeout User For 28 Day")
    #             embed.set_footer(text=message.author.id)
    #             time = datetime.datetime.utcnow()+ datetime.timedelta(days=27)
    #             channel = self.bot.get_channel(803687264110247987)
    #             #await message.author.edit(timeout=time, reason="detection of phishing links")
    #             try:
    #                 await message.delete()
    #             except:
    #                 pass
    #             await channel.send(embed=embed, content="<@&787259553225637889> If link is phishing ban user Fast", view=BanButton(self.bot))
    #             try:
    #                 await message.author.send("phishing has been detected in your message and you have been put on timeout if you think it's mistake Dm any Admin")
    #             except:
    #                 pass
                
async def setup(bot):
    await bot.add_cog(AutoMod(bot))
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
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
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
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(BanButton(self.bot))
        print(f'{self.__class__.__name__} Cog has been loaded\n-----')
    
    @commands.Cog.listener()
    async def on_message(self, message):
        
        if self.bot.automod != True: return
        if message.author.bot: return
        if message.guild.id != 785839283847954433: return

        link = is_link_there(message.content)
        if len(message.mentions) >= 9:
            if message.author.id in [301657045248114690,488614633670967307,413651113485533194,651711446081601545,810041263452848179,457839031909351425]:
                return

            await message.delete()
            await message.channel.send(f"{message.author.mention} have been warned for mentioning more than 10 people in a message")
            await message.author.edit(timed_out_until=discord.utils.utcnow() + datetime.timedelta(hours=10))

        if len(link) > 0:
            r = is_link_bad(link[0])
            if r['badDomain'] == True:
                embed = discord.Embed(description=f"Message Sent by {message.author.mention} Contains known phishing link",color=0xff0000)
                embed.add_field(name="Message", value=f"||{message.content}||")
                embed.add_field(name="Action Taken", value="Timeout User For 28 Day")
                embed.set_footer(text=message.author.id)
                time = datetime.datetime.utcnow()+ datetime.timedelta(days=27)
                channel = self.bot.get_channel(803687264110247987)
                #await message.author.edit(timeout=time, reason="detection of phishing links")
                try:
                    await message.delete()
                except:
                    pass
                await channel.send(embed=embed, content="<@&787259553225637889> If link is phishing ban user Fast", view=BanButton(self.bot))
                try:
                    await message.author.send("phishing has been detected in your message and you have been put on timeout if you think it's mistake Dm any Admin")
                except:
                    pass
                
async def setup(bot):
    await bot.add_cog(AutoMod(bot))
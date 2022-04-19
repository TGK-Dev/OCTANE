from time import time
from discord.ext import commands
import re
import requests
import json
import datetime
import discord

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

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invite_regex = re.compile(r"(?:https?://)?(?:www\.)?(?:discord\.(?:gg|io|me|li)|discordapp\.com/invite)/.+[a-z]")
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__} Cog has been loaded\n-----')
        self.log_channel = self.bot.get_channel(803687195599962162)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id != 935763990670348309: return
        if message.author.bot or message.author.id in self.bot.owner_ids: return
        link_check = re.findall(self.invite_regex, message.content)
        log_channel = await self.bot.config.find(message.guild.id)
        log_channel = self.bot.get_channel(log_channel['mod_log'])

        if link_check:
            ban_link = is_link_bad(link_check[0])
            if ban_link['badDomain'] == True:
                embed = discord.Embed(description=f"Message Sent by {message.author.mention} Contains known phishing link",color=0xff0000)
                embed.add_field(name="Message", value=f"||{message.content}||")
                embed.add_field(name="Action Taken", value="Timeout User For 28 Day")
                embed.set_footer(text=message.author.id)
                await message.author.ban(reason="Phishing Link")
                channel = self.bot.get_channel(803687264110247987)
                await message.author.edit(timeout=time, reason="detection of phishing links")
                try:
                    await message.delete()
                except:
                    pass
                await channel.send(embed=embed, content="<@&787259553225637889> If link is phishing ban user Fast")
                try:
                    await message.author.send("phishing has been detected in your message and you have been put on timeout if you think it's mistake Dm any Admin")
                except:
                    pass
                return
            await message.delete()
            await message.channel.send(f"{message.author.mention} No Invites Allowed", delete_after=10)
            embed = discord.Embed(title="Invite link Tigger", description=f"{message.author.mention} Send invite link in {message.channel.mention}", color=0x00ff00)
            embed.add_field(name="Message", value=message.content, inline=False)
            embed.set_footer(text=f"ID: {message.author.id}")
            embed.timestamp = discord.utils.utcnow()
            await log_channel.send(embed=embed)

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
                await log_channel.send(embed=embed)
                
        print(self.bot.auto_mod_cache)

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
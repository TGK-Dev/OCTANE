from time import time
from discord.ext import commands
from discord import app_commands
import typing
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

class Auto_mod_slash(app_commands.Group):
    def __init__(self):
        super().__init__(name="automod")

    async def rule_auto(self, interaction: discord.Interaction, current: str) -> typing.List[app_commands.Choice[str]]:
        current_rules = [rule for rule in await interaction.guild.fetch_automod_rules()]
        choice = [
            app_commands.Choice(name=rule.name, value=str(rule.id))
            for rule in current_rules if current.lower() in rule.name.lower()
        ]
        return(list(choice[:24]))

    @app_commands.command(name="addword", description="add word new word in block list")
    @app_commands.default_permissions(administrator=True)
    @app_commands.autocomplete(rule_name=rule_auto)
    @app_commands.describe(word='the word to add', rule_name="the rule to add the word to")
    @app_commands.rename(rule_name="rule")
    async def add_word(self, interaction: discord.Interaction, rule_name: str, word: str):
        rule = await interaction.guild.fetch_automod_rule(int(rule_name))
        block_list = rule.trigger.keyword_filter
        if word in block_list:
            await interaction.response.send_message("Word already in block list", ephemeral=True)
            return
        block_list.append(word)
        await rule.edit(trigger=discord.AutoModTrigger(keyword_filter=block_list))
        await interaction.response.send_message("Word added to block list", ephemeral=True)
    
    @app_commands.command(name="removeword", description="remove word from block list")
    @app_commands.default_permissions(administrator=True)
    @app_commands.autocomplete(rule_name=rule_auto)
    @app_commands.describe(word='the word to remove', rule_name="the rule to remove the word from")
    @app_commands.rename(rule_name="rule")
    async def remove_word(self, interaction: discord.Interaction, rule_name: str, word: str):
        rule = await interaction.guild.fetch_automod_rule(int(rule_name))
        block_list = rule.trigger.keyword_filter
        if word not in block_list:
            await interaction.response.send_message("Word not in block list", ephemeral=True)
            return
        block_list.remove(word)
        await rule.edit(trigger=discord.AutoModTrigger(keyword_filter=block_list))
        await interaction.response.send_message("Word removed from block list", ephemeral=True)

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.invite_regex = re.compile(r"(?:https?://)?(?:www\.)?(?:discord\.(?:gg|io|me|li)|discordapp\.com/invite)/.+[a-z]")
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f'{self.__class__.__name__} Cog has been loaded\n-----')
        self.bot.tree.add_command(Auto_mod_slash(), guild=discord.Object(785839283847954433))
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
                
        self.bot.auto_mod_cache

async def setup(bot):
    await bot.add_cog(AutoMod(bot))
from discord import Interaction
from discord.ext import commands
from io import BytesIO
import os
import random
import discord
import asyncio
import datetime

class Start_Gn(discord.ui.View):
    def __init__(self, bot, interaction, number):
        self.bot = bot
        self.interaction = interaction
        self.number = number
        super().__init__(timeout=300)
    
    @discord.ui.button(label="Start Game", style=discord.ButtonStyle.green)
    async def start_game(self, interaction: Interaction, button: discord.Button):
        right_num = random.randint(1, self.number)
        await interaction.response.send_message(f"Right number is: {right_num}", ephemeral=True)

        await interaction.user.send(f"Right Number is: {right_num}")

        button.style = discord.ButtonStyle.blurple
        button.disabled = True
        button.label = str("Started")

        await interaction.message.edit(view=self)

        thread = await interaction.message.create_thread(name="Guess Number Here", auto_archive_duration=60)

        self.bot.dispatch('game_start', interaction.message, thread, right_num)

        self.bot.guess_number[thread.id] = {'thread': thread, 'right_num': right_num, 'guess_num': 0}

        await interaction.channel.send(f"Start guessing the number in thread above, {thread.mention}")
    
    async def on_timeout(self, interaction):
        self.stop()

    async def interaction_check(self ,interaction):
        if interaction.user.id == self.interaction.user.id:
            return True
        else:
            await interaction.response.send_message("You can't start the game, you are not the host", ephemeral=True)

class Invite_Panel(discord.ui.View):
    def __init__(self, staff_invite: discord.Invite, public_invite: discord.Invite):
        super().__init__(timeout=3600)
        self.staff_invite = staff_invite
        self.public_invite = public_invite
    
    @discord.ui.button(label="Public Invite", style=discord.ButtonStyle.green, custom_id="public-invite")
    async def public_invite(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(self.public_invite, ephemeral=True)

    @discord.ui.button(label="Staff-invite", style=discord.ButtonStyle.red, custom_id="staff-invite")
    async def staff_invite(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(self.staff_invite,ephemeral=True)
        else:
            await interaction.response.send_message("You don't have permission to use this button.", ephemeral=True)
    
    
class Req_veriy_code(discord.ui.View):
    def __init__(self, bot):
        self.bot= bot
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Request Code", style=discord.ButtonStyle.green, custom_id="request", emoji="🧾")
    async def request(self, interaction: discord.Interaction, button: discord.ui.Button):
        verify_code  = Make_Verify_Code()

        image = ImageCaptcha().create_captcha_image(verify_code, color="white", background="black")
        file  = discord.File("./captcha.png", filename="captcha.png")

        embed = discord.Embed(title="Captcha", description="Please type the captcha below", color=discord.Color.blue())
        embed.set_image(url=f"attachment://captcha.png")
        try:
            await interaction.user.send(embed=embed)
            await interaction.response.send_message("Please check your DM", ephemeral=True)
        except discord.HTTPException:
            await interaction.response.send_message("open your DM's to send the captcha", ephemeral=True)
        
        
        os.remove('captcha.png')

class Payout_Buttton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Payout", style=discord.ButtonStyle.green, custom_id="payout")
    async def payout(self, interaction: discord.Interaction, button: discord.ui.Button):
        loadin_embed = discord.Embed(description="<a:loading:998834454292344842> | Marking payout...", color=discord.Color.blue())
        await interaction.response.send_message(embed=loadin_embed, ephemeral=True)

        data = await interaction.client.payout.find(interaction.message.id)
        if not data: await interaction.edit_original_response(embed=discord.Embed(description="<:dynoError:1000351802702692442> | Payout not found in Database", color=discord.Color.red()))

        embed = interaction.message.embeds[0]
        embed.remove_field(len(embed.fields)-1)
        embed.add_field(name="Payout Status", value="**<:nat_reply_cont:1011501118163013634> Done**")
        embed.title = "Successfull Payment!"
        embed.color = discord.Color.green()
        embed.add_field(name="Santioned By", value=f"**<:nat_reply_cont:1011501118163013634> {interaction.user.mention}**")
        button.disabled = True
        button.label = "Payout Successfully!"

        
        winner_channel = interaction.client.get_channel(data['channel'])
        winner_message = await winner_channel.fetch_message(data['winner_message_id'])
        
        view = discord.ui.View()
        view.add_item(discord.ui.Button(label=f'Winner Message', url=f"{winner_message.jump_url}"))
        view.add_item(discord.ui.Button(label=f'Payout Queue Message', url=f"{interaction.message.jump_url}"))
        success_embed = discord.Embed(description="<:octane_yes:1019957051721535618> | Payout Marked Successfully!", color=discord.Color.green())
        await interaction.edit_original_response(embed=success_embed, view=view)
        await interaction.message.edit(view=self, embed=embed, content=None)
        await interaction.client.payout.delete(data['_id'])
        
        is_more_payout_pending = await interaction.client.payout.find_many_by_custom({'winner_message_id': data['winner_message_id']})
        if len(is_more_payout_pending) <= 0:
            loading_emoji = await interaction.client.emoji_server.fetch_emoji(998834454292344842)
            paid_emoji = await interaction.client.emoji_server.fetch_emoji(1052528036043558942)
            winner_channel = interaction.client.get_channel(data['channel'])
            try:
                winner_message = await winner_channel.fetch_message(data['winner_message_id'])
                await winner_message.remove_reaction(loading_emoji, interaction.client.user)
                await winner_message.add_reaction(paid_emoji)
            except Exception as e:
                pass                

    async def on_error(self, interaction: Interaction, error: Exception, item: discord.ui.Item):
        try:
            await interaction.response.send_message(f"Error: {error}", ephemeral=True)
        except:
            await interaction.edit_original_response(content=f"Error: {error}")

    async def interaction_check(self, interaction: Interaction):
        dank_manager_role = discord.utils.get(interaction.guild.roles, id=989947301126631504)
        if dank_manager_role in interaction.user.roles:
            return True
        else:
            embed = discord.Embed(title="Error", description="You don't have permission to use this button", color=discord.Color.red())
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False

class ButtonOnCooldown(commands.CommandError):
  def __init__(self, retry_after: float):
    self.retry_after = retry_after

def key(interaction: discord.Interaction):
  return interaction.user
class level_check(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)
        self.cd = commands.CooldownMapping.from_cooldown(1.0, 300, key)    
    
    async def interaction_check(self, interaction: discord.Interaction):
        retry_after = self.cd.update_rate_limit(interaction)
        if retry_after:
            raise ButtonOnCooldown(retry_after)
        
        return True
    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item):
        if isinstance(error, ButtonOnCooldown):
            seconds = int(error.retry_after)
            unit = 'second' if seconds == 1 else 'seconds'
            await interaction.response.send_message(f"You're on cooldown for {seconds} {unit}!", ephemeral=True)
        else:
            await super().on_error(interaction, error, item)

    @discord.ui.button(label='Check Level', style=discord.ButtonStyle.green, custom_id="LEVEL:CHECK")
    async def count(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Getting data...", ephemeral=True)
        data = await self.bot.Amari_api.fetch_user(interaction.guild.id, interaction.user.id)
        embed = discord.Embed(description=f"**Name:** {interaction.user.mention}\n**Level:** {data.level}\n**XP:** {data.exp}\n**Weeklyexp:** {data.weeklyexp}", color=interaction.user.color)
        embed.timestamp = discord.utils.utcnow()
        embed.set_footer(text=f"{interaction.user.name}#{interaction.user.discriminator}", icon_url=self.bot.user.avatar.url)
        await interaction.edit_original_response(content=None, embed=embed)

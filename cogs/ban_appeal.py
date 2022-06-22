import discord
from discord import app_commands
from discord.ext import commands
from discord import Interaction
import datetime

class Support(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Appeal", style=discord.ButtonStyle.red, custom_id="APPEAL")
    async def support(self, interaction: Interaction, button: discord.Button):

        await interaction.response.send_message("Creating a Appeal ticket...", ephemeral=True)

        data = await interaction.client.config.find(interaction.guild.id)
        if not data:
            return await interaction.edit_original_message(content="Setup is not complete, please run `setup`", ephemeral=True)
        
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, view_channel=False),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, view_channel=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, view_channel=True, attach_files=True, send_messages=True)
        }
        channel = await interaction.guild.create_text_channel(name="{} appeal".format(interaction.user.name), reason="Creating appeal channel", overwrites=overwrites, category=interaction.channel.category)

        log_embed = discord.Embed()
        log_embed.set_author(name=f"{interaction.user.name}#{interaction.user.discriminator}", icon_url=interaction.user.avatar.url)
        log_embed.add_field(name="Ticket Owner", value=f"{interaction.user.mention}")
        log_embed.add_field(name="Ticket Created", value=f"{channel.name}")
        log_embed.add_field(name="Ticket Type", value="Appeal")
        log_embed.color = 0x00FF00

        log_channel = interaction.client.get_channel(data['Tickets']['log_channel'])
        log_msg = await log_channel.send(embed=log_embed)

        data = {
            '_id': channel.id,
            'ticket_owner': interaction.user.id,
            'added_roles': [],
            'added_users': [],
            'type': 'appeal',
            'created_at': datetime.datetime.utcnow(),
            'status': 'open',
            'log_message_id': log_msg.id
        }

        #await interaction.client.ticket.insert(data)
        await interaction.edit_original_message(content=f"Your ticket has been created, you can view it here: {channel.mention}")
        #embed = discord.Embed(description="```\nPlease wait for a moderator to review your ticket\nPlease Send Answers of Following Qestions\n\n1. Why did you get banned?\n\n2. Why do you think your appeal should be accepted?\n\n3. Is there anything else you would like for us to know?\n\n```", color=0x00FF00)
        embed = discord.Embed(description="**Please wait for a staff to review your ticket.**\n\n> Do let us know why do you think your appeal should be accepted?", color=0x00FF00)
        await channel.send(embed=embed, content=interaction.user.mention)
        

class BanAppeal(commands.Cog, name="Ban Appeal", description="Easy way to add Ban Appeal"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(Support())
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    # @commands.Cog.listener()
    # async def on_member_join(self, member):
    #     main_guild = self.bot.get_guild(785839283847954433)
    #     if member.guild.id != 988761284956799038: return
    #     if member.bot: return
        
    #     if member.id in [main_member.id for main_member in main_guild.members]:
    #         main_guild_member = main_guild.get_member(member.id)
    #         if main_guild_member.guild_permissions.administrator:
    #             return
    #         else:
    #             try:
    #                 await member.send("Your account has not banned in main server.")
    #             except discord.HTTPException:
    #                 pass
                
    #             await member.kick(reason="Your account has not banned in main server.")
    #     try:
    #         user = await self.bot.fetch_user(member.id)
    #         banned = await main_guild.fetch_ban(user)
    #     except discord.NotFound:
    #         try:
    #             await member.send("Your account has not banned in main server.")
    #         except discord.HTTPException:
    #             pass
            
    #         await member.kick(reason="Your account has not banned in main server.")

    @app_commands.command(name="approve", description="Approve a ban appeal")
    @app_commands.guild_only()
    @app_commands.guilds(988761284956799038)
    @app_commands.default_permissions(administrator=True)
    async def approve(self, interaction: Interaction, user: discord.Member):
        main_guild = await self.bot.fetch_guild(785839283847954433)
        try:
            ban = await main_guild.fetch_ban(user)
            if ban:
                await main_guild.unban(user, reason="Ban Appeal Approved by {}".format(interaction.author.name))
                await interaction.response.send_message("Ban Appeal Approved", ephemeral=True)
                await interaction.channel.send(f"{user.mention} Your ban has been lifted by {interaction.author.mention}")
        except discord.NotFound:
            await interaction.response.send_message("User is not banned")
            return        

    @app_commands.command(name="deny", description="Deny a ban appeal")
    @app_commands.guild_only()
    @app_commands.guilds(988761284956799038)
    @app_commands.default_permissions(administrator=True)
    async def deny(self, interaction: Interaction, user: discord.Member, reason: str=None):
        main_guild = await self.bot.fetch_guild(785839283847954433)
        try:
            await user.send("Your ban appeal has been denied\n`Reason:` {}".format(reason))
        except discord.HTTPException:
            pass
        
        await interaction.response.send_message("User Appeal has been denied")

    @app_commands.command(name="setup", description="Set up ticket channel")
    @app_commands.guild_only()
    @app_commands.guilds(988761284956799038)
    @app_commands.default_permissions(administrator=True)
    async def setup(self, interaction: Interaction):
        embed = discord.Embed(title="Appeal Center", description="This channel is for for [Main TGK Server](https://discord.gg/NmD4JGCaNc) to use for ban appeals only", color=0xFF0000)
        embed.set_footer(text="TGK Ban Appeal",icon_url=interaction.guild.icon.url)
        await interaction.channel.send(embed=embed, view=Support())

        await interaction.response.send_message("Setup complete")

async def setup(bot):
    await bot.add_cog(BanAppeal(bot))

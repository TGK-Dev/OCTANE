import discord
import datetime
#from utils.checks import checks
import asyncio
import chat_exporter
import io
from discord import Interaction
from .models import RenameTicket
import re
class Ticket_Control(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Open", custom_id="Control:Open", style=discord.ButtonStyle.gray, disabled=True, emoji="🔓")
    async def Open(self, interaction: discord.Interaction ,button: discord.Button):
        await interaction.response.defer(thinking=True)
        ticket_data = await self.bot.config.find(interaction.guild.id)
        ticket_data = ticket_data['Tickets']
        
        data = await self.bot.ticket.find(interaction.channel.id)
        ticket_owner = interaction.guild.get_member(int(data['ticket_owner']))
        if ticket_owner == None:
            return await interaction.followup.send("Ticket owner is not in the server, you may delete the ticket", ephemeral=False)
        elif data is None:
            return await interaction.followup.send("Ticket does not exist", ephemeral=False)
        await interaction.channel.edit(sync_permissions=True)

        overrite = discord.PermissionOverwrite()
        overrite.view_channel = True
        overrite.send_messages = True
        overrite.read_messages = True
        overrite.attach_files = True

        await interaction.channel.set_permissions(ticket_owner, overwrite=overrite)

        for i in data['added_roles']:
            role = discord.utils.get(interaction.guild.roles, id=int(i))
            await interaction.channel.set_permissions(role, overwrite=overrite)
        
        for i in data['added_users']:
            user = self.bot.get_user(int(i))
            await interaction.channel.set_permissions(user, overwrite=overrite)

        data['status'] = "open"
        await self.bot.ticket.upsert(data)

        for role in ticket_data[data['type']]['supprot_roles']:
            role = discord.utils.get(interaction.guild.roles, id=int(role))
            await interaction.channel.set_permissions(role, overwrite=overrite)
        await interaction.followup.send(embed=discord.Embed(description=f"<:allow:819194696874197004> | Ticket re-opened by {interaction.user.mention}", color=0x2f3136))

        log_embed = discord.Embed(color=0x00FF00)
        log_channel = self.bot.get_channel(ticket_data['log_channel'])
        log_embed.set_author(name=f"{interaction.user.name}#{interaction.user.discriminator}", icon_url=interaction.user.avatar.url)
        log_embed.add_field(name="Ticket", value=interaction.channel.name)
        log_embed.add_field(name="Action", value=f"Opend {interaction.channel.name}")
        await log_channel.send(embed=log_embed)

        for button in self.children:
            if button.custom_id == "Control:Close":
                button.disabled = False
            if button.custom_id == "Control:Open":
                button.disabled = True
        
        await interaction.message.edit(view=self)

    @discord.ui.button(label="Close", custom_id="Control:Close", style=discord.ButtonStyle.gray, emoji="🔒")
    async def Close(self, interaction: discord.Interaction ,button: discord.Button):
        await interaction.response.defer(ephemeral=False, thinking=True)
        ticket_data = await self.bot.config.find(interaction.guild.id)

        ticket_data = ticket_data['Tickets']
        if interaction.channel.category.id != ticket_data["category"]:
            return await interaction.followup.send("This is not a ticket channel", ephemeral=True)
        
        data = await self.bot.ticket.find(interaction.channel.id)
        ticket_owner = self.bot.get_user(int(data['ticket_owner']))
        await interaction.channel.edit(sync_permissions=True)

        overrite = discord.PermissionOverwrite()
        overrite.view_channel = False

        staff_overrite = discord.PermissionOverwrite()
        staff_overrite.view_channel = True
        staff_overrite.send_messages = True
        staff_overrite.read_messages = True
        staff_overrite.attach_files = True

        for i in data['added_roles']:
            role = discord.utils.get(interaction.guild.roles, id=int(i))
            await interaction.channel.set_permissions(role, overwrite=overrite)
        
        for i in data['added_users']:
            user = self.bot.get_user(int(i))
            await interaction.channel.set_permissions(user, overwrite=overrite)

        for role in ticket_data[data['type']]['supprot_roles']:
            role = discord.utils.get(interaction.guild.roles, id=int(role))
            await interaction.channel.set_permissions(role, overwrite=staff_overrite)

        data['status'] = "closed"
        await self.bot.ticket.update(data)

        await interaction.followup.send(embed=discord.Embed(description=f"<:allow:819194696874197004> | Ticket closed by {interaction.user.mention}", color=0x2f3136))

        log_embed = discord.Embed(color=0xFF0000)
        log_channel = self.bot.get_channel(ticket_data['log_channel'])
        log_embed.set_author(name=f"{interaction.user.name}#{interaction.user.discriminator}", icon_url=interaction.user.avatar.url)
        log_embed.add_field(name="Ticket", value=interaction.channel.name)
        log_embed.add_field(name="Action", value=f"Closed {interaction.channel.name}")
        await log_channel.send(embed=log_embed)

        for button in self.children:
            if button.custom_id == "Control:Close":
                button.disabled = True
            if button.custom_id == "Control:Open":
                button.disabled = False
        
        await interaction.message.edit(view=self)
    
    @discord.ui.button(label="Secure", custom_id="Control:Secure", style=discord.ButtonStyle.gray, emoji="🔐")
    async def Secure(self, interaction: discord.Interaction ,button: discord.Button):
        ticket_info = await self.bot.ticket.find(interaction.channel.id)
        await interaction.response.defer(ephemeral=False, thinking=True)
        message = await interaction.followup.send("Securing ticket...")

        if ticket_info is None:
            return await interaction.followup.send("Ticket Not Found")
        
        await interaction.channel.edit(sync_permissions=True)
        ticket_owner = interaction.guild.get_member(int(ticket_info['ticket_owner']))
        if not ticket_owner:
            return await interaction.followup.send("Ticket Owner Not Found")
        
        overwrite = discord.PermissionOverwrite()
        overwrite.view_channel = False
        overwrite.read_messages = False
        overwrite.send_messages = False
        overwrite.attach_files = False

        for i in interaction.channel.overwrites:
            await interaction.channel.set_permissions(i, overwrite=overwrite)
        
        owner_owrite = discord.PermissionOverwrite()
        owner_owrite.view_channel = True
        owner_owrite.send_messages = True
        owner_owrite.read_messages = True
        owner_owrite.attach_files = True

        await interaction.channel.set_permissions(ticket_owner, overwrite=owner_owrite)

        await message.edit(content=None,embed=discord.Embed(description=f"<:allow:819194696874197004> | Ticket secured by {interaction.user.mention}", color=0x00FF00))

        button.disabled = True
        await interaction.message.edit(view=self)
    
    @discord.ui.button(label="Save", custom_id="Control:Save", style=discord.ButtonStyle.green, emoji="📩")
    async def Save(self, interaction: discord.Interaction ,button: discord.Button):
        await interaction.response.defer(thinking=True)
        ticket_data = await self.bot.config.find(interaction.guild.id)
        ticket_data = ticket_data['Tickets']
        message = await interaction.followup.send("Saving ticket ...")
        topic = interaction.channel.name

        transcript = await chat_exporter.export(interaction.channel, limit=None,tz_info="Asia/Kolkata")

        if transcript is None:
            await interaction.followup.send("An Error Occured, Try Again Later")
            return
        
        transcript_file = discord.File(io.BytesIO(transcript.encode()),filename=f"transcript-{interaction.channel.name}.html")

        transcript_log_channel = self.bot.get_channel(ticket_data["transcript"])

        link_msg = await transcript_log_channel.send(content=f"{interaction.channel.name} | {topic}",file=transcript_file)

        link_button = discord.ui.View()
        url = f"https://codebeautify.org/htmlviewer?url={link_msg.attachments[0].url}"
        link_button.add_item(discord.ui.Button(label='View Transcript', url=url))

        await link_msg.edit(view=link_button)

    
        await message.edit(content=None,embed=discord.Embed(description=f"<:save:819194696874197004> | Transcript Saved", color=0x00FF00),view=link_button)

        log_embed = discord.Embed(color=0x00FF00)
        log_channel = self.bot.get_channel(ticket_data['log_channel'])
        log_embed.set_author(name=f"{interaction.user.name}#{interaction.user.discriminator}", icon_url=interaction.user.avatar.url)
        log_embed.add_field(name="Ticket", value=interaction.channel.name)
        log_embed.add_field(name="Action", value=f"Saved Transcript")
        await log_channel.send(embed=log_embed)
        ticket_info = await self.bot.ticket.find(interaction.channel.id)
        log_msg = await log_channel.fetch_message(ticket_info['log_message_id'])
        embed = log_msg.embeds[0]
        embed.add_field(name="Transcript", value=f"[Link](<{link_msg.attachments[0].url}>)")
        await log_msg.edit(embed=embed)

        for button in self.children:
            if button.custom_id == "Control:Save":
                #button.disabled = True
                pass
        
        await interaction.message.edit(view=self)
    
    @discord.ui.button(label="Delete", custom_id="Control:Delete", style=discord.ButtonStyle.red, emoji="🗑️")
    async def Delete(self, interaction: discord.Interaction ,button: discord.Button):
        data = await self.bot.ticket.find(interaction.channel.id)
        config_data = await self.bot.config.find(interaction.guild.id)
        if interaction.channel.category.id != config_data['Tickets']['category']:
            return await interaction.response.send_message("This is not a ticket channel", ephemeral=True)
        ticket_data = config_data['Tickets']
        await interaction.response.defer(thinking=True)
        msg = await interaction.followup.send("Deleting this ticket in 10s `type fs` to cancel this command")
        
        try:
            stop_m = await self.bot.wait_for('message', check=lambda m: m.author.id == interaction.user.id and m.channel.id == interaction.channel.id and m.content.lower() == "fs", timeout=10)
            await stop_m.add_reaction("✅")
            return await msg.edit(content="Ok cancelling the command")

        except asyncio.TimeoutError:
            
            user_in_channel = {}
            async for message in interaction.channel.history(limit=None):
                if message.author.id in user_in_channel.keys():
                    user_in_channel[message.author.id] += 1
                else:
                    user_in_channel[message.author.id] = 1

            log_channel = self.bot.get_channel(ticket_data['log_channel'])
            log_message = await log_channel.fetch_message(data['log_message_id'])
            embed = log_message.embeds[0]
            users, i = "", 1

            for key, value in user_in_channel.items():
                users += f"{i}. <@{key}> - {value}\n"
                i += 1

            embed.add_field(name="Users in Ticket", value=users)
            await log_message.edit(embed=embed)

            await self.bot.ticket.delete(interaction.channel.id)
            await interaction.channel.delete()

            log_embed = discord.Embed(color=0xFF0000)
            log_channel = self.bot.get_channel(ticket_data['log_channel'])
            log_embed.set_author(name=f"{interaction.user.name}#{interaction.user.discriminator}", icon_url=interaction.user.avatar.url)
            log_embed.add_field(name="Ticket", value=interaction.channel.name)
            log_embed.add_field(name="Action", value=f"Deleted {interaction.channel.name}")
            await log_channel.send(embed=log_embed)

    @discord.ui.button(label="Rename Ticket", custom_id="Control:Rename", style=discord.ButtonStyle.green, emoji="📝")
    async def Rename(self, interaction: discord.Interaction ,button: discord.Button):
        await interaction.response.send_modal(RenameTicket(self.bot, interaction))

    @discord.ui.button(label="Add Shero", custom_id="Control:shero", style=discord.ButtonStyle.gray, emoji="🤖")
    async def add_shero(self, interaction: discord.Interaction ,button: discord.Button) -> None:

        shero = interaction.guild.get_member(692570006969516032)
        if not shero:
            await interaction.response.send_message(f"Shero is not in the server. Please contact the owner", ephemeral=True)
            return

        await interaction.response.defer(thinking=True)
        data = await self.bot.ticket.find(interaction.channel.id)
        if data['type'] == 'partnership':

            if shero.bot:
                overwrite = discord.PermissionOverwrite()
                overwrite.view_channel = True
                overwrite.send_messages = True
                overwrite.read_messages = True
                overwrite.attach_files = True
                await interaction.channel.set_permissions(shero, overwrite=overwrite)
                await interaction.followup.send(embed=discord.Embed(description=f"<:allow:819194696874197004> | {shero.mention} added to the ticket", color=0x2f3136))
                button.disabled = True
                await interaction.message.edit(view=self)
        else:
            await interaction.followup.send("This is not a partnership ticket", ephemeral=True)
    
    async def interaction_check(self, interaction: discord.Interaction):
        if interaction.user.guild_permissions.manage_messages:
            return True
        else:
            await interaction.response.send_message("You do not have permission to run this command", ephemeral=True)
            return False

class Support_model(discord.ui.Modal, title="Support Ticket Form"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)
    
    qestion = discord.ui.TextInput(label="Question:", placeholder="What's your question? or your problem?", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        data = await self.bot.config.find(interaction.guild.id)
        ticket_data = data['Tickets']

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, view_channel=False),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, view_channel=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, view_channel=True, attach_files=True, send_messages=True)
        }

        for role in ticket_data['support']['supprot_roles']:
            role = discord.utils.get(interaction.guild.roles, id=int(role))
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, view_channel=True, attach_files=True, send_messages=True)

        if ticket_data['category'] != None:
            channel = await interaction.guild.create_text_channel(name=f"{interaction.user.display_name} support ticket", category=self.bot.get_channel(ticket_data['category']), overwrites=overwrites)
        else:
            channel = await interaction.guild.create_text_channel(name=f"{interaction.user.display_name} support ticket", overwrites=overwrites, category=interaction.channel.category)
        
        embed = discord.Embed(title=f"Hi {interaction.user.display_name}, Welcome to Server Support",
                                  color=0x008000,
                                  description="Kindly wait patiently. A staff member will assist you shortly.\nIf you're looking to approach a specific staff member, ping the member once. Do not spam ping any member or role.\n\nThank you.")
        embed.set_footer(text="Developed and Owned by Jay & utki007")
        embed.add_field(name="Reason for opening a ticket", value=self.qestion.value if self.qestion.value else "Not Provaided", inline=False)

        await interaction.followup.send(f"Your support ticket is now available at {channel.mention}")

        log_embed = discord.Embed()
        log_embed.set_author(name=f"{interaction.user.name}#{interaction.user.discriminator}", icon_url=interaction.user.avatar.url)
        log_embed.add_field(name="Ticket Owner", value=f"{interaction.user.mention}")
        log_embed.add_field(name="Ticket Created", value=f"{channel.name}")
        log_embed.add_field(name="Ticket Type", value="Support")
        log_embed.color = 0x00FF00

        log_channel = self.bot.get_channel(ticket_data['log_channel'])
        log_msg = await log_channel.send(embed=log_embed)

        data = {
            '_id': channel.id,
            'ticket_owner': interaction.user.id,
            'added_roles': [],
            'added_users': [],
            'type': 'support',
            'created_at': datetime.datetime.utcnow(),
            'status': 'open',
            'log_message_id': log_msg.id
        }

        await self.bot.ticket.insert(data)
        View = Ticket_Control(self.bot)
        if data['type'] == "support":
            for button in View.children:
                if button.custom_id == "Control:shero":
                    button.disabled = False
                    break                                
        
        msg = await channel.send(embed=embed, content=f"{interaction.user.mention} | <@&{ticket_data['support']['ping_role']}>",view=View)
        await msg.pin()
    
    async def on_error(self, error: Exception, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(f"An Error Occured. {error}\nContact Admin/Owner", ephemeral=True)
class Partnership_model(discord.ui.Modal, title="Partnership Ticket Form"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)
    
    server_name = discord.ui.TextInput(label="Server Name", placeholder="Enter Server Name your representing", custom_id="server:name")
    server_invite = discord.ui.TextInput(label="Server Invite", placeholder="Enter Server Invite Link,", custom_id="server:link")
    partership_type = discord.ui.TextInput(label="Partnership Type", placeholder="Enter Partnership Type (heist, event, etc)", custom_id="server:type:partnership")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        data = await self.bot.config.find(interaction.guild.id)
        ticket_data = data['Tickets']

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, view_channel=False),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, view_channel=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, view_channel=True, attach_files=True, send_messages=True)
        }

        for role in ticket_data['partner_ship']['supprot_roles']:
            role = discord.utils.get(interaction.guild.roles, id=int(role))
            if role:
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, view_channel=True, attach_files=True, send_messages=True)

        if ticket_data['category'] != None:
            channel = await interaction.guild.create_text_channel(name=f"{interaction.user.display_name} partnership ticket", category=self.bot.get_channel(ticket_data['category']), overwrites=overwrites)
        else:
            channel = await interaction.guild.create_text_channel(name=f"{interaction.user.display_name} partnership ticket", overwrites=overwrites, category=interaction.channel.category)
        
        embed = discord.Embed(title=f"Hi {interaction.user.display_name}, Welcome to Server Partnership",
                                  color=0x008000,
                                  description="Kindly wait patiently. A staff member will assist you shortly.\nIf you're looking to approach a specific staff member, ping the member once. Do not spam ping any member or role.\n\nThank you.")
        embed.set_footer(text="Developed and Owned by Jay & utki007")

        try:
            invite = await self.bot.fetch_invite(self.server_invite.value)
            info_data = f"**Server Invite:** {invite.url}\n**Server Name:** {self.server_name.value}\n**Server ID:** {invite.guild.id}\n**Partnership Type:** {self.partership_type.value}"
        except:
            info_data = f"**Server Invite:** {self.server_invite.value}\n**Server Name:** {self.server_name.value}\n**Server ID:** Didn't Get Done\n**Partnership Type:** {self.partership_type.value}"
            pass
            
        log_embed = discord.Embed()
        log_embed.set_author(name=f"{interaction.user.name}#{interaction.user.discriminator}", icon_url=interaction.user.avatar.url)
        log_embed.add_field(name="Ticket Owner", value=f"{interaction.user.mention}")
        log_embed.add_field(name="Ticket Created", value=f"{channel.name}")
        log_embed.add_field(name="Ticket Type", value="Partnership")
        log_embed.color = 0x00FF00

        log_channel = self.bot.get_channel(ticket_data['log_channel'])
        log_msg = await log_channel.send(embed=log_embed)

        data = {
            '_id': channel.id,
            'ticket_owner': interaction.user.id,
            'added_roles': [],
            'added_users': [],
            'type': 'partnership',
            'created_at': datetime.datetime.utcnow(),
            'status': 'open',
            'log_message_id': log_msg.id,
        }

        await self.bot.ticket.insert(data)
        
        msg = await channel.send(embed=embed, content=f"{interaction.user.mention} | <@&{ticket_data['partner_ship']['ping_role']}>",view=Ticket_Control(self.bot))
        info_m = await channel.send(info_data)
        await info_m.pin()
        await msg.pin()

        await interaction.followup.send(f"Your Partnership Ticket has been created.{channel.mention}")

class Nickname_model(discord.ui.Modal, title="Nickname Ticket Form"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)
    
    nickname = discord.ui.TextInput(label="Nickname", placeholder="Enter Nickname", custom_id="nickname", style=discord.TextStyle.short, required=True, max_length=32)

    async def on_submit(self, interaction: discord.Interaction):
        new_name = self.nickname.value
        #check if name has anything other than space a-z and 0-9 using re
        if re.search(r'[^a-zA-Z0-9 ]', new_name):
            await interaction.response.send_message(f"Nickname can only contain a-z, A-Z, 0-9 and spaces.", ephemeral=True)
        else:
            await interaction.response.send_message("Please wait while we process your request.", ephemeral=True)
            try:
                await interaction.user.edit(nick=new_name)
                await interaction.edit_original_message(content=f"applied nickname {new_name}")
            except discord.HTTPException:
                await interaction.edit_original_message(content="Failure to change nickname. Please try again later. or contact a staff member.")

class Ticket_main(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)
        url = "https://dyno.gg/form/99ad4f31"
        self.add_item(discord.ui.Button(label='Ban Appeal', url=url))
    
    @discord.ui.button(label='Server Support', style=discord.ButtonStyle.red, custom_id='persistent_view:red', emoji="<:support:837272254307106849>")
    async def support(self, interaction: discord.Interaction ,button: discord.Button):
        await interaction.response.send_modal(Support_model(self.bot))
    
    @discord.ui.button(label='Partnership ', style=discord.ButtonStyle.green, custom_id='persistent_view:partner_ship', emoji="<:partner:837272392472330250>")
    async def partnership(self, interaction: discord.Interaction ,button: discord.Button):
        await interaction.response.send_modal(Partnership_model(self.bot))

    @discord.ui.button(label="Change Nickname", style=discord.ButtonStyle.blurple, custom_id='persistent_view:nickname', emoji="<:TGK_POGGIES:942065551092641853>")
    async def nickname(self, interaction: discord.Interaction ,button: discord.Button):
        await interaction.response.send_modal(Nickname_model(self.bot))

    async def interaction_check(self, interaction):
        data = self.bot.blacklist_users
        if interaction.user.id in data:
            await interaction.response.send_message("You are blacklisted from using this bot.", ephemeral=True)
            return False
        
        else:

            data = await self.bot.ticket.find_many_by_custom({'ticket_owner': interaction.user.id})
            if interaction.user.guild_permissions.manage_messages:
                return True
            if len(data) >= 2:
                await interaction.response.send_message("You already have maxinum tickets open.", ephemeral=True)
                return False
            else:
                return True
        
        

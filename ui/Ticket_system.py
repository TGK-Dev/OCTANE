import discord
import datetime
#from utils.checks import checks
import asyncio
import chat_exporter
import io
from discord import Interaction

async def update_embed(interaction: Interaction, data: dict, name:str):
    panel = data['panels'][name]
    embed = discord.Embed(title=f"{name} Settings", color=discord.Color.blurple())
    Support_roles = ""
    if len(panel['support_role']) > 0:
        for role in panel['support_role']:
            role = interaction.guild.get_role(int(role))
            if role:
                Support_roles += f"{role.name} | {role.id}\n"
    else:
        Support_roles = "None"

    Ping_role = ""
    if panel['ping_role']:
        role = interaction.guild.get_role(int(panel['ping_role']))
        if role:
            Ping_role = f"{role.name} | {role.id}"
    else:
        Ping_role = "None"
    embed.add_field(name="Role Settings", value=f"> **Support Roles:**\n```\n{Support_roles}\n```\n> **Ping Role:**\n```\n{Ping_role}\n```", inline=False)
    embed.add_field(name="Info Settings", value=f"> **Description**\n```\n{panel['description']}\n```", inline=False)
    Modal_Settings = ""
    if panel['modal']:
        Modal_Settings += f"Question: {panel['modal']['question']}\nAnswer Type: {panel['modal']['type']}"
    else:
        Modal_Settings = "None"
    embed.add_field(name="Modal Settings", value=f"```\n{Modal_Settings}\n```", inline=False)
    Other = ""
    if panel['emoji']:
        Other += f"Emoji: {panel['emoji']}\n"
    if panel['color']:
        Other += f"Color: {panel['color']}"
    if Other:
        embed.add_field(name="Other Settings", value=f"```\n{Other}\n```", inline=False)
    else:
        embed.add_field(name="Other Settings", value="```\nNone\n```", inline=False)
    await interaction.followup.send("Panel Roles Updated", ephemeral=True)

class Ticket_Control_Panel(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Open", style=discord.ButtonStyle.primary, custom_id="OPEN:TICKET", emoji="🔓")
    async def open_ticket(self, interaction: Interaction, button: discord.Button):
        data = await self.bot.tickets.find(interaction.channel.id)
        ticket_config = await self.bot.ticket_system.find(interaction.guild.id)
        if data is None:
            return await interaction.response.send_message("This channel is not a ticket channel.", ephemeral=True)
        if data['status'] == "open":
            await interaction.response.send_message("This ticket is already open.", ephemeral=True)
            return await interaction.response.edit_message(view=self)

        if data['status'] == "closed":
            embed = discord.Embed(description="<a:loading:998834454292344842> | Opening ticket...", color=discord.Color.blurple())
            await interaction.response.send_message(embed=embed, ephemeral=False)
            ticket_owner = interaction.guild.get_member(data['user'])
            overrite = discord.PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True, attach_files=True)
            await interaction.channel.set_permissions(ticket_owner, overwrite=overrite)
            for i in data['add_roles']:
                await interaction.channel.set_permissions(interaction.guild.get_role(i), overwrite=overrite)
            for i in data['add_users']:
                await interaction.channel.set_permissions(interaction.guild.get_member(i), overwrite=overrite)

            data['status'] = "open"
            await self.bot.tickets.update(data)

            embed.description = "<:dynosuccess:1000349098240647188> | Ticket opened!"
            embed.color = discord.Color.green()
            await interaction.edit_original_response(embed=embed)
            await interaction.message.edit(view=self)

            log_channel = interaction.guild.get_channel(ticket_config['logging'])
            log_embed = discord.Embed(title="Ticket opened", description=f"{interaction.channel.mention} opened by {interaction.user.mention}",)
            log_embed.timestamp = datetime.datetime.utcnow()
            log_embed.color = discord.Color.blurple()
            if log_channel is not None:
                await log_channel.send(embed=log_embed)

    @discord.ui.button(label="Close", style=discord.ButtonStyle.primary, custom_id="CLOSE:TICKET", emoji="🔒")
    async def close_ticket(self, interaction: Interaction, button: discord.Button):
        data = await self.bot.tickets.find(interaction.channel.id)
        ticket_config = await self.bot.ticket_system.find(interaction.guild.id)
        if data is None:
            return await interaction.response.send_message("This channel is not a ticket channel.", ephemeral=True)
        if data['status'] == "closed":
            await interaction.response.send_message("This ticket is already closed.", ephemeral=True)
            button.disabled = True
            return await interaction.response.edit_message(view=self)

        if data['status'] == "open":

            embed = discord.Embed(description="<a:loading:998834454292344842> | Closing ticket...", color=discord.Color.blurple())
            await interaction.response.send_message(embed=embed, ephemeral=False)
            ticket_owner = interaction.guild.get_member(data['user'])
            overrite = discord.PermissionOverwrite(read_messages=False, send_messages=False, read_message_history=False, attach_files=False)
            await interaction.channel.set_permissions(ticket_owner, overwrite=overrite)
            for i in data['add_roles']:
                await interaction.channel.set_permissions(interaction.guild.get_role(i), overwrite=overrite)
            for i in data['add_users']:
                await interaction.channel.set_permissions(interaction.guild.get_member(i), overwrite=overrite)
            data['status'] = "closed"
            await self.bot.tickets.update(data)

            embed.description = "<:dynosuccess:1000349098240647188> | Ticket closed!"
            embed.color = discord.Color.green()
            await interaction.edit_original_response(embed=embed)
            await interaction.message.edit(view=self)

            log_channel = interaction.guild.get_channel(ticket_config['logging'])
            log_embed = discord.Embed(title="Ticket closed", description=f"{interaction.channel.mention} Ticket closed by {interaction.user.mention}")
            log_embed.timestamp = datetime.datetime.utcnow()
            log_embed.color = discord.Color.red()
            if log_channel is not None:
                await log_channel.send(embed=log_embed)
    
    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger, custom_id="DELETE:TICKET", emoji="🗑")
    async def delete_ticket(self, interaction: Interaction, button: discord.Button):
        ticket_data = await self.bot.ticket_system.find(interaction.guild.id)
        data = await self.bot.tickets.find(interaction.channel.id)
        if data is None:
            return await interaction.response.send_message("This channel is not a ticket channel.", ephemeral=True)

        embed = discord.Embed(description="<a:loading:998834454292344842> | Saving ticket...", color=discord.Color.blurple())
        await interaction.response.send_message(embed=embed, ephemeral=False)

        transcript = await chat_exporter.export(interaction.channel, limit=None,tz_info="Asia/Kolkata")
        if transcript is None:
            return await interaction.edit_original_response("Failed to save ticket.")
        
        transcript_file = discord.File(io.BytesIO(transcript.encode()),filename=f"transcript-{interaction.channel.name}.html")
        transcript_log_channel = self.bot.get_channel(ticket_data["transcripts"])

        if transcript_log_channel:
            link_msg = await transcript_log_channel.send(content=f"{interaction.channel.name}",file=transcript_file)
            link_button = discord.ui.View()
            url = f"https://codebeautify.org/htmlviewer?url={link_msg.attachments[0].url}"
            link_button.add_item(discord.ui.Button(label='View Transcript', url=url))
            await link_msg.edit(view=link_button)

        embed.description = "<:dynosuccess:1000349098240647188> | Ticket saved!\n<a:loading:998834454292344842> | Deleting ticket in 10 seconds send fs to cancel."
        embed.color = discord.Color.green()
        await interaction.edit_original_response(embed=embed)
        try:
            stop_m = await self.bot.wait_for("message", check=lambda m: m.author == interaction.user and m.content.lower() == "fs" and m.channel.id == interaction.channel.id, timeout=10)
            msg = await interaction.original_response()
            await msg.add_reaction("<:dynoError:1000351802702692442>")
            embed.description = "<:dynoError:1000351802702692442> | Cancelled."
            embed.color = discord.Color.red()
            await interaction.edit_original_response(embed=embed)
            return
        except asyncio.TimeoutError:
            user_in_channel = {}
            async for message in interaction.channel.history(limit=None):
                if message.author.id in user_in_channel.keys():
                    user_in_channel[message.author.id] += 1
                else:
                    user_in_channel[message.author.id] = 1
            
            log_channel = interaction.guild.get_channel(ticket_data['logging'])
            log_message = await log_channel.fetch_message(data['logging_message'])
            users ,i = "", 1
            for key, value in user_in_channel.items():
                users += f"{i}. <@{key}> - {value}\n"
                i += 1

            log_message.embeds[0].add_field(name="Users in Ticket", value=users, inline=False)
            await log_message.edit(embed=log_message.embeds[0])
            await interaction.channel.delete()
            log_embed = discord.Embed(title="Ticket deleted", description=f"{interaction.channel.name} Ticket deleted by {interaction.user.mention}")
            log_embed.timestamp = datetime.datetime.utcnow()
            log_embed.color = discord.Color.red()
            if log_channel is not None:
                await log_channel.send(embed=log_embed)

            await self.bot.tickets.delete(interaction.channel.id)
class Ticket_Control(discord.ui.View):
    def __init__(self, data: dict):
        super().__init__(timeout=None)
        self.data = data
        style = None
        for i, value in data.items():
            if value['color'] == "green":
                style = discord.ButtonStyle.green
            elif value['color'] == "red":
                style = discord.ButtonStyle.red
            elif value['color'] == "blue" or "blurple":
                style = discord.ButtonStyle.blurple
            elif value['color'] == "grey" or "default" or "gray":
                style = discord.ButtonStyle.grey
            btn = Panel_Button(label=i, style=style, custom_id="persistent_view:{}".format(i), emoji=str(value['emoji']) if value['emoji'] is not None else None)
            self.add_item(btn)

class Panel_Button(discord.ui.Button):
    async def callback(self, interaction: Interaction):
        if self.label == "Partnership":
            await interaction.response.send_modal(Partnership_Qestion(interaction))
            return
        data = await interaction.client.ticket_system.find(interaction.guild.id)
        panel = data['panels'][self.label]
        modal = General_Qestions(interaction, self.label)
        style = discord.TextStyle.paragraph if panel['modal']['type'] == "long" or "paragraph" else discord.TextStyle.short
        modal.add_item(discord.ui.TextInput(label=panel['modal']['question'], style=style, custom_id="GEN:QUESTIONS", required=True,max_length=1000))
        await interaction.response.send_modal(modal)

class Partnership_Qestion(discord.ui.Modal):
    def __init__(self, interaction: discord.Interaction):
        self.interaction = interaction
        super().__init__(timeout=None, title="Server Info")

    server_name = discord.ui.TextInput(label="Server Name", placeholder="Enter Server Name your representing", custom_id="server:name")
    server_invite = discord.ui.TextInput(label="Server Invite", placeholder="Enter Server Invite Link,", custom_id="server:link")
    partership_type = discord.ui.TextInput(label="Partnership Type", placeholder="Enter Partnership Type (heist, event, etc)", custom_id="server:type:partnership")

    async def on_submit(self, interaction: Interaction):

        embed = discord.Embed(description="Please wait while we process your question", color=discord.Color.green())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        data = await self.interaction.client.ticket_system.find(interaction.guild.id)
        panel = data['panels']["Partnership"]
        try:
            inv = self.server_invite.value
            invite = inv.split("/")
            code = invite[len(invite)-1]
            invite = await interaction.client.fetch_invite(code)
            info_data = f"**Server Invite:** {invite.url}\n**Server Name:** {self.server_name.value}\n**Server ID:** {invite.guild.id}\n**Partnership Type:** {self.partership_type.value}"
        except:
            info_data = f"**Server Invite:** {self.server_invite.value}\n**Server Name:** {self.server_name.value}\n**Server ID:** Didn't Get Done\n**Partnership Type:** {self.partership_type.value}"
            pass
        
        permissons = {
            interaction.user : discord.PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True, attach_files=True),
            interaction.guild.default_role : discord.PermissionOverwrite(read_messages=False, send_messages=False, read_message_history=False, attach_files=False),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True, attach_files=True, manage_channels=True,)
        }
        for i in panel['support_role']:
            permissons[interaction.guild.get_role(i)] = discord.PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True, attach_files=True)
        
        channel = await interaction.guild.create_text_channel(name=f"{interaction.user.display_name}-ticket", category=interaction.client.get_channel(data['catogory']) if data['catogory'] else interaction.channel.category, overwrites=permissons)
        embed = discord.Embed(title=f"{interaction.user.display_name} Welcome to {panel['key']}",description="Kindly wait patiently. A staff member will assist you shortly.\nIf you're looking to approach a specific staff member, ping the member once. Do not spam ping any member or role.\n\nThank you.")
        embed.set_footer(text="Developed by: JAY#0138 & utki007#0007", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        content = f"{interaction.user.mention}"
        if panel['ping_role'] is not None:
            content += f" | <@&{panel['ping_role']}>"
        msg = await channel.send(content=content,embed=embed, view=Ticket_Control_Panel(interaction.client))
        server_info_msg = await channel.send(content=info_data)
        await msg.pin()
        await server_info_msg.pin()

        ticket_data = {'_id': channel.id, 'user': interaction.user.id, 'add_roles': [], 'add_users': [], 'panel': panel['key'], 'logging_message': None, 'status': 'open', 'logging': None, 'question': info_data}
        
        log_channel = interaction.guild.get_channel(data['logging'])
        log_embed = discord.Embed()
        log_embed.set_author(name=f"{interaction.user.display_name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
        log_embed.add_field(name="Ticket Owner", value=interaction.user.mention)
        log_embed.add_field(name="Ticket Panel", value=panel['key'])
        log_embed.add_field(name="Ticket Channel", value=f"{channel.mention} | {channel.name} | {channel.id}")
        log_embed.timestamp = datetime.datetime.utcnow()

        if log_channel:
            msg = await log_channel.send(embed=log_embed)
            ticket_data['logging_message'] = msg.id
            
        await self.interaction.client.tickets.insert(ticket_data)
        await interaction.edit_original_response(content=f"Your ticket has been created. You can view it here: {channel.mention}")

class General_Qestions(discord.ui.Modal):
    def __init__(self, interaction: discord.Interaction, panel: str):
        super().__init__(timeout=None, title="General Questions")
        self.interaction = interaction
        self.panel = panel

    async def on_submit(self, interaction: discord.Interaction):
        for child in self.children:
            
            if child.custom_id == "GEN:QUESTIONS":
                embed = discord.Embed(description="Please wait while we process your question", color=discord.Color.green())
                embed.add_field(name="Your Reason", value=child.value)
                await interaction.response.send_message(embed=embed, ephemeral=True)
                data = await self.interaction.client.ticket_system.find(interaction.guild.id)
                panel = data['panels'][self.panel]

                permissons = {
                    interaction.user : discord.PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True, attach_files=True),
                    interaction.guild.default_role : discord.PermissionOverwrite(read_messages=False, send_messages=False, read_message_history=False, attach_files=False),
                    interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True, attach_files=True, manage_channels=True,)
                }
                for i in panel['support_role']:
                    permissons[interaction.guild.get_role(i)] = discord.PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True, attach_files=True)
            

                channel = await interaction.guild.create_text_channel(name=f"{interaction.user.display_name}-ticket", category=interaction.client.get_channel(data['catogory']) if data['catogory'] else interaction.channel.category, overwrites=permissons)

                embed = discord.Embed(title=f"{interaction.user.display_name} Welcome to {panel['key']}",description="Kindly wait patiently. A staff member will assist you shortly.\nIf you're looking to approach a specific staff member, ping the member once. Do not spam ping any member or role.\n\nThank you.")
                embed.set_footer(text="Developed by: JAY#0138 & utki007#0007", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
                embed.add_field(name=panel['modal']['question'], value=child.value)
                content = f"{interaction.user.mention}"
                if panel['ping_role'] is not None:
                    content += f" | <@&{panel['ping_role']}>"
                msg = await channel.send(content=content,embed=embed, view=Ticket_Control_Panel(interaction.client))
                await msg.pin()
                
                ticket_data = {'_id': channel.id, 'user': interaction.user.id, 'add_roles': [], 'add_users': [], 'panel': self.panel, 'logging_message': None, 'status': 'open', 'logging': None, 'question': child.value}
                
                log_channel = interaction.guild.get_channel(data['logging'])
                log_embed = discord.Embed()
                log_embed.set_author(name=f"{interaction.user.display_name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
                log_embed.add_field(name="Ticket Owner", value=interaction.user.mention)
                log_embed.add_field(name="Ticket Panel", value=panel['key'])
                log_embed.add_field(name="Ticket Qestions", value=child.value)
                log_embed.add_field(name="Ticket Channel", value=f"{channel.mention} | {channel.name} | {channel.id}")
                log_embed.timestamp = datetime.datetime.utcnow()

                if log_channel:
                    msg = await log_channel.send(embed=log_embed)
                    ticket_data['logging_message'] = msg.id
                    
                await self.interaction.client.tickets.insert(ticket_data)
                await interaction.edit_original_response(content=f"Your ticket has been created. You can view it here: {channel.mention}")


class Panel_edit(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, data: dict, name: str ,message: discord.Message=None):
        super().__init__(timeout=120)
        self.interaction = interaction
        self.data = data
        self.message = message
        self.name = name
    
    @discord.ui.button(label="Roles Settings", style=discord.ButtonStyle.gray, emoji="<:mention:991734732188553337>", custom_id="EDIT:PANEL:ROLES")
    async def edit_panel_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = Ticket_Panel_Roles(interaction,self.name, self.data)
        default = [str(role) for role in self.data['panels'][self.name]['support_role']]

        modal.add_item(discord.ui.TextInput(required=False,label="Support Role", style=discord.TextStyle.paragraph, custom_id="PANEL:ROLES:QUESTIONS", 
            max_length=1000, default=",".join(default) if len(default) > 0 else None, placeholder="Please state the roles you want to be able to support, seperated by a comma."))
        modal.add_item(discord.ui.TextInput(required=False,label="Ping Roles", style=discord.TextStyle.short, custom_id="PANEL:ROLES:PING", default=self.data['panels'][self.name]['ping_role'] if self.data['panels'][self.name]['ping_role'] is not None else None, placeholder="Please state the role you want to ping on ticket creation."))

        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Info Settings", style=discord.ButtonStyle.gray, emoji="<:IconInsights:751160378800472186>", custom_id="EDIT:PANEL:INFO")
    async def edit_panel_info(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = Ticket_Panel_Info(interaction, self.name,self.data)
        modal.add_item(discord.ui.TextInput(label="Description", style=discord.TextStyle.paragraph, custom_id="PANEL:INFO:DESCRIPTION", default=self.data['panels'][self.name]['description'] if self.data['panels'][self.name]['description'] is not None else None, placeholder="Please state the description of the panel."))
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Questions Settings", style=discord.ButtonStyle.gray, emoji="<:StageIconRequests:1005075865564106812>", custom_id="EDIT:PANEL:QUESTIONS")
    async def edit_panel_questions(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = Ticket_Panel_Questions(interaction, self.data, self.name)
        modal.add_item(discord.ui.TextInput(label="Questions", style=discord.TextStyle.paragraph, custom_id="PANEL:QUESTIONS:QUESTIONS", default=self.data['panels'][self.name]['modal']['question'] if self.data['panels'][self.name]['modal']['question'] is not None else None, placeholder="Please state the questions you want to ask the user, seperated by a comma."))
        modal.add_item(discord.ui.TextInput(label="Answers type", style=discord.TextStyle.short, custom_id="PANEL:QUESTIONS:ANSWERS", placeholder="select from [short, paragraph]", default=self.data['panels'][self.name]['modal']['type']))
        await interaction.response.send_modal(modal)        

    @discord.ui.button(label="Other Settings", style=discord.ButtonStyle.gray, emoji="<:ServerVerifiedSchoolHub:1005081309598711849>", custom_id="EDIT:PANEL:SETTINGS")
    async def edit_panel_settings(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = Ticket_Panel_edit_Other(interaction, self.name, self.data)
        modal.add_item(discord.ui.TextInput(label="Emoji", style=discord.TextStyle.paragraph, custom_id="PANEL:SETTINGS:NAME", default=self.data['panels'][self.name]['emoji'] if self.data['panels'][self.name]['emoji'] is not None else None, placeholder="Please state the emoji you want to use for the panel."))
        modal.add_item(discord.ui.TextInput(label="Color", style=discord.TextStyle.short, custom_id="PANEL:SETTINGS:COLOR", default=self.data['panels'][self.name]['color'] if self.data['panels'][self.name]['color'] is not None else None, placeholder="Please state the color of the panel."))
        await interaction.response.send_modal(modal)

    async def interaction_check(self, interaction: Interaction):
        if interaction.user.id != self.interaction.user.id:
            await interaction.response.send_message("Your not allowed to use those buttons.", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        for butoon in self.children:
            butoon.disabled = True
            await self.message.edit(content="Panel edit timed out.", view=self)



class Ticket_Panel_edit_Other(discord.ui.Modal):
    def __init__(self, interaction: Interaction, name: str, data: dict):
        super().__init__(timeout=None, title=f"Editing {name} Extra Info")
        self.data = data
        self.interaction = interaction
        self.name = name
    
    async def on_submit(self, interaction: Interaction):
        for child in self.children:
            if child.label == "Emoji":
                self.data['panels'][self.name]['emoji'] = child.value
            if child.label == "Color":
                if child.value == "":
                    self.data['panels'][self.name]['color'] = None
                if child.value in ['red', 'green', 'blue', 'grey']:
                    self.data['panels'][self.name]['color'] = child.value
                else:
                    await interaction.response.send(f"{child.value} is not a valid color choice from [red, green, blue, grey]", ephemeral=True)
                    return
            
        await self.interaction.client.tickets.update(self.data)
        await interaction.response.defer(thinking=True, ephemeral=True)
        await update_embed(interaction, self.data)


class Ticket_Panel_edit_Other(discord.ui.Modal):
    def __init__(self, interaction: Interaction, name: str, data: dict):
        super().__init__(timeout=None, title=f"Editing {name} Extra Info")
        self.data = data
        self.interaction = interaction
        self.name = name
    
    async def on_submit(self, interaction: Interaction):
        for child in self.children:
            if child.label == "Emoji":
                self.data['panels'][self.name]['emoji'] = child.value
            if child.label == "Color":
                if child.value == "":
                    self.data['panels'][self.name]['color'] = None
                if child.value in ['red', 'green', 'blue', 'grey', 'gray']:
                    self.data['panels'][self.name]['color'] = child.value
            
        await interaction.response.defer(thinking=True, ephemeral=True)
        await interaction.client.ticket_system.update(self.data)

        await update_embed(interaction, self.data, self.name)

class Ticket_Panel_Questions(discord.ui.Modal):
    def __init__(self, interaction: discord.Interaction, data: dict, name: str):
        super().__init__(timeout=None, title=f"Edit {name} Questions")
        self.interaction = interaction
        self.data = data
        self.name = name
    
    async def on_submit(self, interaction: discord.Interaction):
        for child in self.children:
            if child.label == "Questions":                
                self.data['panels'][self.name]['modal']['question'] = child.value
        
            if child.label == "Answers type":
                if child.value not in ['short', 'paragraph', 'long']:
                    await interaction.response.send_message(f"Please select from [short, paragraph, long]")
                    return
        
        await interaction.response.defer(thinking=True, ephemeral=True)
        await interaction.client.ticket_system.update(self.data)
        await update_embed(interaction, self.data, self.name)


class Ticket_Panel_Info(discord.ui.Modal):
    def __init__(self, interaction: Interaction, name: str, data: dict):
        super().__init__(timeout=None, title=f"Editing {name} description")
        self.data = data
        self.interaction = interaction
        self.name = name
    
    async def on_submit(self, interaction: Interaction):
        for child in self.children:
            if child.label == "Description":
                self.data['panels'][self.name]['description'] = child.value
                await interaction.client.ticket_system.update(self.data)
                await interaction.response.defer(thinking=True, ephemeral=True)
                await update_embed(interaction, self.data, self.name)
                break


class Ticket_Panel_Roles(discord.ui.Modal):
    def __init__(self, interaction: Interaction, name: str, data: dict):
        super().__init__(timeout=None, title=f"Editing {name} Roles")
        self.data = data
        self.interaction = interaction
        self.name = name
    
    async def on_submit(self, interaction: Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)
        for child in self.children:
            
            if child.label == "Support Role":
                new_support_role = []
                new_role = child.value.split(",")

                for role in new_role:
                    role = interaction.guild.get_role(int(role))
                    if role is not None:
                        new_support_role.append(role.id)

                self.data['panels'][self.name]['support_role'] = new_support_role
            
            if child.label == "Ping Roles":

                try:
                    role = interaction.guild.get_role(int(child.value))
                    if role is not None:
                        self.data['panels'][self.name]['ping_role'] = role.id
                    else:
                        await interaction.followup.send("Invalid Role ID for Ping Roles")
                except ValueError:
                    pass
            
        await interaction.client.ticket_system.update(self.data)
        await update_embed(interaction, self.data, self.name)

class MyModal(discord.ui.Modal):
    name = discord.ui.TextInput(label='Name')
    foo = discord.ui.Select(options=[discord.SelectOption(label='option 1'), discord.SelectOption(label='option 2')])

    async def on_submit(self, interaction):
        await interaction.response.send_message(f'Thanks for your response', ephemeral=True)

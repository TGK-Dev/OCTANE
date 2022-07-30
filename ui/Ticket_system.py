import discord
import datetime
#from utils.checks import checks
import asyncio
import chat_exporter
import io
from discord import Interaction

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
            await interaction.edit_original_message(embed=embed)
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
            await interaction.edit_original_message(embed=embed)
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
            return await interaction.edit_original_message("Failed to save ticket.")
        
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
        await interaction.edit_original_message(embed=embed)
        try:
            stop_m = await self.bot.wait_for("message", check=lambda m: m.author == interaction.user and m.content.lower() == "fs" and m.channel.id == interaction.channel.id, timeout=10)
            msg = await interaction.original_message()
            await msg.add_reaction("<:dynoError:1000351802702692442>")
            embed.description = "<:dynoError:1000351802702692442> | Cancelled."
            embed.color = discord.Color.red()
            await interaction.edit_original_message(embed=embed)
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
        style = discord.ButtonStyle.gray
        for i, value in data.items():
            if value['color']:
                if value['color'] == 'green':
                   style = discord.ButtonStyle.green
                elif value['color'] == 'red':
                    style = discord.ButtonStyle.red
                elif value['color'] == 'blurple' or 'blue':
                    style = discord.ButtonStyle.blurple
            btn = Panel_Button(label=i, style=style, custom_id="persistent_view:{}".format(i), emoji=str(value['emoji']) if value['emoji'] is not None else None)
            self.add_item(btn)

class Panel_Button(discord.ui.Button):
    async def callback(self, interaction: Interaction):
        await interaction.response.send_modal(General_Qestions(interaction, self.label))


class General_Qestions(discord.ui.Modal):
    def __init__(self, interaction: discord.Interaction, panel: str):
        super().__init__(timeout=None, title="General Questions")
        self.interaction = interaction
        self.panel = panel
    
    gen_qestions = discord.ui.TextInput(label="Please State Your Question", style=discord.TextStyle.paragraph, custom_id="GEN:QUESTIONS", required=True, max_length=1000)

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(description="Please wait while we process your question", color=discord.Color.green())
        embed.add_field(name="Your Question", value=self.gen_qestions.value)
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
    

        channel = await interaction.guild.create_text_channel(name=f"{panel['key']}-{interaction.user.display_name}", category=interaction.client.get_channel(data['catogory']) if data['catogory'] else interaction.channel.category, overwrites=permissons)

        embed = discord.Embed(title=f"{interaction.user.display_name} Welcome to {panel['key']}",description="Kindly wait patiently. A staff member will assist you shortly.\nIf you're looking to approach a specific staff member, ping the member once. Do not spam ping any member or role.\n\nThank you.")
        embed.set_footer(text="Developed by: JAY#0138 & utki007#0007", icon_url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.add_field(name="Question", value=self.gen_qestions.value)
        content = f"{interaction.user.mention}"
        if panel['ping_role'] is not None:
            content += f" | <@&{panel['ping_role']}>"
        print(content)
        msg = await channel.send(content=content,embed=embed, view=Ticket_Control_Panel(interaction.client))
        await msg.pin()
        
        ticket_data = {'_id': channel.id, 'user': interaction.user.id, 'add_roles': [], 'add_users': [], 'panel': self.panel, 'logging_message': None, 'status': 'open', 'logging': None, 'question': self.gen_qestions.value}
        
        log_channel = interaction.guild.get_channel(data['logging'])
        log_embed = discord.Embed()
        log_embed.set_author(name=f"{interaction.user.display_name}", icon_url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
        log_embed.add_field(name="Ticket Owner", value=interaction.user.mention)
        log_embed.add_field(name="Ticket Panel", value=panel['key'])
        log_embed.add_field(name="Ticket Qestions", value=self.gen_qestions.value)
        log_embed.add_field(name="Ticket Channel", value=f"{channel.mention} | {channel.name} | {channel.id}")
        log_embed.timestamp = datetime.datetime.utcnow()

        if log_channel:
            msg = await log_channel.send(embed=log_embed)
            ticket_data['logging_message'] = msg.id
            
        await self.interaction.client.tickets.insert(ticket_data)
        await interaction.edit_original_message(content=f"Your ticket has been created. You can view it here: {channel.mention}")



import discord
import datetime

class PartnerShip_model(discord.ui.Modal, title="PartnerShip Infomations"):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)

    server_name = discord.ui.TextInput(label="Server Name", placeholder="Enter Server Name your representing", custom_id="server:name")
    server_invite = discord.ui.TextInput(label="Server Invite", placeholder="Enter Server Invite Link,", custom_id="server:link")
    partership_type = discord.ui.TextInput(label="Partnership Type", placeholder="Enter Partnership Type (heist, event, etc)", custom_id="server:type:partnership")

    async def on_submit(self, interaction: discord.Interaction):
        config = await self.bot.config.find(interaction.guild.id)
        staff_role = discord.utils.get(interaction.guild.roles, id=config['support_role'])
        pm_role = discord.utils.get(interaction.guild.roles, id=config['pm_role'])

        if config and config['ticket_category'] is not None:
            staff_role = discord.utils.get(interaction.guild.roles, id=config['support_role'])

            override = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, view_channel=False),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True, view_channel=True),
                staff_role: discord.PermissionOverwrite(read_messages=True, view_channel=True),
                pm_role: discord.PermissionOverwrite(read_messages=True, view_channel=True),
                interaction.user: discord.PermissionOverwrite(read_messages=True, view_channel=True, attach_files=True)
            }

            channel = await interaction.guild.create_text_channel(name=f"{interaction.user.name} Partership",category=self.bot.get_channel(config['ticket_category']),overwrites=override,
                topic=f"ID: {interaction.user.id}")

        else:

            override = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, view_channel=False),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True, view_channel=True),
                interaction.user: discord.PermissionOverwrite(read_messages=True, view_channel=True, attach_files=True),
                staff_role: discord.PermissionOverwrite(read_messages=True, view_channel=True)
            }
            channel = await interaction.guild.create_text_channel(name=f"{interaction.user.name} Partership",overwrites=override, category=interaction.channel.category)
        
        embed = discord.Embed(title=f"Hi {interaction.user.display_name}, Welcome to Server Support",
                                  color=0x008000,
                                  description="Kindly wait patiently. A staff member will assist you shortly.\nIf you're looking to approach a specific staff member, ping the member once. Do not spam ping any member or role.\n\nThank you.")
        embed.set_footer(text="Developed and Owned by Jay & utki007")

        await channel.send(embed=embed, content=f"{interaction.user.mention} | `{pm_role.mention}`")

        invite = await self.bot.fetch_invite(self.server_invite.value)
        
        info_m = await channel.send(f"**Server Invite:** {invite.url}\n**Server Name:** {self.server_name.value}\n**Server ID:** {invite.guild.id}\n**Partnership Type:** {self.partership_type.value}")

        await info_m.pin()

        await interaction.response.send_message(f"Your Ticket is Ready at: {channel.mention}", ephemeral=True)

        log_embed = discord.Embed()
        log_embed.set_author(name=f"{interaction.user.name}#{interaction.user.discriminator}", icon_url=interaction.user.avatar.url)
        log_embed.add_field(name="Ticket Owner", value=f"{interaction.user.mention}")
        log_embed.add_field(name="Ticket Created", value=f"{channel.mention}")
        log_embed.add_field(name="Ticket Type", value="Partnership")
        log_embed.color = 0x00FF00

        log_channel = self.bot.get_channel(config['ticket_log_channel'])
        log_msg = await log_channel.send(embed=log_embed)

        data = {
            '_id': channel.id,
            'ticket_owner': interaction.user.id,
            'added_roles': [],
            'added_users': [],
            'type': 'partnership',
            'created_at': datetime.datetime.utcnow(),
            'status': 'open',
            'log_message_id': log_msg.id
        }

        await self.bot.ticket.upsert(data)

class Ticket_panel(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)
        url = 'https://dyno.gg/form/99ad4f31'
        self.add_item(discord.ui.Button(label='Ban Appeal', url=url))

    @discord.ui.button(label='Server Support', style=discord.ButtonStyle.red, custom_id='persistent_view:red', emoji="<:support:837272254307106849>")
    async def support(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        config = await self.bot.config.find(interaction.guild.id)
        staff_role = discord.utils.get(interaction.guild.roles, id=config['support_role'])

        if config and config['ticket_category'] is not None:
            staff_role = discord.utils.get(interaction.guild.roles, id=config['support_role'])

            override = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, view_channel=False),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True, view_channel=True),
                staff_role: discord.PermissionOverwrite(read_messages=True, view_channel=True),
                interaction.user: discord.PermissionOverwrite(read_messages=True, view_channel=True, attach_files=True)
            }

            channel = await interaction.guild.create_text_channel(name=f"{interaction.user.name} Support",category=self.bot.get_channel(config['ticket_category']),overwrites=override,
                topic=f"ID: {interaction.user.id}")
        else:
            override = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, view_channel=False),
                interaction.guild.me: discord.PermissionOverwrite(read_messages=True, view_channel=True),
                interaction.user: discord.PermissionOverwrite(read_messages=True, view_channel=True, attach_files=True),
                staff_role: discord.PermissionOverwrite(read_messages=True, view_channel=True)
            }
            channel = await interaction.guild.create_text_channel(name=f"{interaction.user.name} Partership",overwrites=override, category=interaction.channel.category)
        
        embed = discord.Embed(title=f"Hi {interaction.user.display_name}, Welcome to Server Support",
                                  color=0x008000,
                                  description="Kindly wait patiently. A staff member will assist you shortly.\nIf you're looking to approach a specific staff member, ping the member once. Do not spam ping any member or role.\n\nThank you.")
        embed.set_footer(text="Developed and Owned by Jay & utki007")

        await channel.send(embed=embed, content=f"{interaction.user.mention} | `{staff_role.mention}`")

        await interaction.followup.send(f"Your Ticket is created at {channel.mention}")

        log_embed = discord.Embed()
        log_embed.set_author(name=f"{interaction.user.name}#{interaction.user.discriminator}", icon_url=interaction.user.avatar.url)
        log_embed.add_field(name="Ticket Owner", value=f"{interaction.user.mention}")
        log_embed.add_field(name="Ticket Created", value=f"{channel.mention}")
        log_embed.add_field(name="Ticket Type", value="Support")
        log_embed.color = 0x00FF00

        log_channel = self.bot.get_channel(config['ticket_log_channel'])
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

        await self.bot.ticket.upsert(data)


    @discord.ui.button(label='Partnership ', style=discord.ButtonStyle.green, custom_id='persistent_view:partner_ship', emoji="<:partner:837272392472330250>")
    async def partnership(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_modal(PartnerShip_model(self.bot))

    @discord.ui.button(label='Want bot like me ?', style=discord.ButtonStyle.blurple, custom_id='persistent_view:custom_bot', emoji="🤖")
    async def custom_bot(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = discord.Embed(description="Yes you can get a Bot like me With very cheap price with hosting\nJust Dm <@488614633670967307> or <@301657045248114690> and We don't take any bot currency as payment")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def interaction_check(self ,interaction):
        data = self.bot.blacklist_users
        if interaction.user.id in data:
            await interaction.response.send_message("Your Blacklisted from bot", ephemeral=True)
        else:
            data = await self.bot.ticket.find_many_by_custom({'ticket_owner': interaction.user.id})
            print(data)
            if len(data) >= 2:
                await interaction.response.send_message("You have a ticket open, please close it before creating a new one", ephemeral=True)
                return False
            else:
                return True
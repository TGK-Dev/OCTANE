import discord
from utils.converter import millify

class Member_view(discord.ui.View):
    def __init__(self, bot,member: discord.Member, interaction: discord.Interaction):
        self.member = member
        self.author = interaction.user
        self.message = None
        self.bot = bot
        super().__init__(timeout=120)
    
    @discord.ui.select(placeholder="Select Page", custom_id="MEMBER_VIEW", max_values=1,
                        options=[
                        discord.SelectOption(label="Profile", value="profile"),
                        discord.SelectOption(label="Badge", value="badge", emoji="<:bage:991740849664819332>"),
                        discord.SelectOption(label="Donation", value="donation", emoji="<:donate:992042322583883877>"),
                        discord.SelectOption(label="Roles", value="roles", emoji="<:mention:991734732188553337>"),
                        discord.SelectOption(label="Levels", value="level", emoji=None),
                        discord.SelectOption(label="Votes", value="votes")])
    async def member_view(self, interaction: discord.Interaction, select: discord.ui.Select):
        choice = select.values[0]
        match choice:
            case "profile":
                
                embed = discord.Embed(title=f"User Info - {self.member.name}#{self.member.discriminator}")
                embed.set_thumbnail(url=self.member.avatar.url if self.member.avatar else self.member.default_avatar.url)

                embed.add_field(name="<:authorized:991735095587254364> ID:", value=self.member.id)
                embed.add_field(name="<:displayname:991733326857654312> Display Name:", value=self.member.display_name)

                embed.add_field(name="<:bot:991733628935610388> Bot Account:", value=self.member.bot)                

                embed.add_field(name="<:settings:991733871118917683> Account creation:", value=self.member.created_at.strftime('%d/%m/%Y %H:%M:%S'))
                embed.add_field(name="<:join:991733999477203054> Server join:", value=self.member.joined_at.strftime('%d/%m/%Y %H:%M:%S'))
                await interaction.response.edit_message(embed=embed)

            case "badge":

                embed = discord.Embed(title=f"Badges - {self.member.name}#{self.member.discriminator}")
                badge = ""            
                if self.member.id in interaction.client.owner_ids:
                    badge += "Developer <:dev:992045587488833659>\n"
                    badge += "Owner <:owner:992045640479686667>\n"
                if self.member.guild_permissions.administrator:
                    badge += "Admin <a:admin:992043062874361866>\n"
                if self.member.guild_permissions.manage_messages:
                    badge += "Moderator <:mod:992043856197595187>\n"
                if discord.utils.get(self.member.guild.roles, id=818129661325869058) in self.member.roles:
                    badge += "Staff Team <:staff:992044132644175934>\n"
                if self.member.premium_since is not None:
                    badge += "Booster <a:booster:992039182442704966>\n"                    
                moneydata = await self.bot.money.find(self.member.id)
                
                if moneydata is not None:
                    if moneydata['bal'] > 500000000:
                        badge += "500Mil Donor<a:500dono:992046271923765361>\n"
                if discord.utils.get(self.member.guild.roles, id=931072410365607946) in self.member.roles:
                    badge += "Frist 50 Members <a:real_og:992048421974315051>\n"
                
                if discord.utils.get(self.member.guild.roles, id=786884615192313866) in self.member.roles:
                    badge += "Voted <:TGK_vote:942521024476487741>"
                if len(badge) > 0:
                    embed.description = badge
                else:
                    embed.description = "No Badges"
                await interaction.response.edit_message(embed=embed)

            case "donation":
                data = await self.bot.money.find(self.member.id)
                embed = discord.Embed(title=f"Donation - {self.member.name}#{self.member.discriminator}")
                if data is None:
                    embed.description = f"No Donation"

                    await interaction.response.edit_message(embed=embed)
                elif data is not None:
                    donation = f"**Total Donation: **`⏣ {millify(data['bal'])}`"
                    embed.description = donation
                    if len(data['event']) > 0:
                        event_dono = ""
                        for event in data['event']:
                            if event['bal'] > 0:
                                event_dono += f"**{event['name']}:** ⏣`{millify(event['bal'])}`\n"
                            if len(event_dono) > 0:
                                embed.add_field(name="Event Donations", value=event_dono)
                            
                    await interaction.response.edit_message(embed=embed)

            case "roles":
                embed = discord.Embed(title=f"Roles - {self.member.name}#{self.member.discriminator}")
                roles = ""
                list_role = sorted(self.member.roles, reverse=True)
                for role in list_role:
                    if len(roles) <= 2000:
                        roles += f"{role.mention} | `{role.id}`\n"
                    else:
                        embed.set_footer(text="And More ....")
                        break
                embed.description = roles
                await interaction.response.edit_message(embed=embed)
            
            case "level":
                embed = discord.Embed(title=f"Level - {self.member.name}#{self.member.discriminator}")
                level = await self.bot.Amari_api.fetch_user(interaction.guild.id, self.member.id)
                if level is None:
                    embed.description = f"No Level"
                elif level is not None:
                    embed.description = f"**Level:** `{level.level}`\n"
                    embed.description += f"**Weekly:** `{level.weeklyexp}`\n"
                await interaction.response.edit_message(embed=embed)
            
            case "votes":
                embed = discord.Embed(title=f"Votes - {self.member.name}#{self.member.discriminator}")
                votes_data = await self.bot.votes.find(self.member.id)
                if votes_data is None:
                    embed.description = f"No Votes"
                elif votes_data is not None:
                    embed.description = f"**Total Votes:** {votes_data['votes']}\n"
                    embed.description += f"**Vote Streak:** {votes_data['streak']}\n"
                    embed.description += f"**Last Vote:** <t:{round(votes_data['last_vote'].timestamp())}:R>"

                await interaction.response.edit_message(embed=embed)


    async def on_timeout(self):
        for i in self.children:
            i.disabled=True        
        await self.message.edit(view=self)

    async def interaction_check(self, interaction: discord.Interaction):
        if self.author.id == interaction.user.id:
            return True
        else:
            await interaction.response.send_message(f"Use /whois from {self.bot.user.mention} to view your own profile", ephemeral=True)
        
        def make_check():
            guild = interaction.guild
            member = guild.member
            #sort member by member.joined_at oldest to newest
            list_member = sorted(guild.members, key=lambda m: m.joined_at)
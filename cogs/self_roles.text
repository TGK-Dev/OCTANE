import discord
import datetime
from discord.ext import commands

game_role = [795711140108697630, 795711130378829835]
bot_role = [801392998465404958, 791713762041266226, 842809745802526730]
server_role = [835442987382210570, 836925033506275399,
               793535450597294101, 804055217108680725, 791347199119327252]
giveaways_roles = [800685251276963861, 822021066548969482, 848809346972516363]
partnership_roles = [797448080223109120, 810593886720098304]
dank_roles = [804068344612913163, 804069957528584212,
              806795854475165736, 799517544674230272]


class self_role_menu_game(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='B.G.M.I', style=discord.ButtonStyle.green, emoji="<a:TGK_militarywalk:842665232831873034>", custom_id="self_role_men:bgmi")
    async def self_role_bgmi(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        role = discord.utils.get(guild.roles, id=int(game_role[0]))
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Remvoed", ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Added", ephemeral=True)

    @discord.ui.button(label='Valorant', style=discord.ButtonStyle.green, emoji="<:valorant:882139310655160321>", custom_id="self_role_menu:Valorant")
    async def self_role_valorant(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        role = discord.utils.get(guild.roles, id=int(game_role[1]))
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Remvoed", ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Added", ephemeral=True)

    @discord.ui.button(label="Check Roles", style=discord.ButtonStyle.blurple, emoji="<:TGK_check:851521037544062996>", custom_id="self_role_menu:game:check")
    async def self_role_check_game(self, button: discord.ui.View, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        has_role = []
        for ids in game_role:
            role = discord.utils.get(guild.roles, id=int(ids))
            if role in user.roles:
                has_role.append(role.mention)

        if len(has_role) == 0:
            roles = "None"
        else:
            roles = ",".join(has_role)

        await interaction.response.send_message(f"You have {roles} from Selected Menu", ephemeral=True)

    @discord.ui.button(label="Back To Menu", style=discord.ButtonStyle.red, emoji="🔙", custom_id="self_role_menu:game:return")
    async def self_role_return_game(self, button: discord.ui.View, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Select Your Menu from here", view=self_role_menu_main())

    @discord.ui.button(label="End Interaction", style=discord.ButtonStyle.red, emoji="<:pepeexit:790189030569934849>", custom_id="self_role_menu:game:exit")
    async def self_role_end_game(self, button: discord.ui.View, interaction: discord.Interaction):
        for button in self.children:
            button.disabled = True

        await interaction.response.edit_message(view=self)


class self_role_menu_bot(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Dank Memer", style=discord.ButtonStyle.green, emoji="<a:rarepepe:801693036911263744>", custom_id="self_role_menu:dank")
    async def self_role_dank(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        role = discord.utils.get(guild.roles, id=int(bot_role[0]))
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Remvoed", ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Added", ephemeral=True)

    @discord.ui.button(label="Casino", style=discord.ButtonStyle.green, emoji="<a:TGK_slots:842628623571091457>", custom_id="self_role_menu:casino")
    async def self_role_casino(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        role = discord.utils.get(guild.roles, id=int(bot_role[1]))
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Remvoed", ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Added", ephemeral=True)

    @discord.ui.button(label="Mudae", style=discord.ButtonStyle.green, emoji="<a:TGK_animegirl:842809462708240384>", custom_id="self_role_menu:mudae")
    async def self_role_mudae(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        role = discord.utils.get(guild.roles, id=int(bot_role[2]))
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Remvoed", ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Added", ephemeral=True)

    @discord.ui.button(label="Check Roles", style=discord.ButtonStyle.blurple, emoji="<:TGK_check:851521037544062996>", custom_id="self_role_menu:bot:check")
    async def self_role_check_bot(self, button: discord.ui.View, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        has_role = []
        for ids in bot_role:
            role = discord.utils.get(guild.roles, id=int(ids))
            has_role.append(role.mention)

        if len(has_role) == 0:
            roles = "None"
        else:
            roles = ",".join(has_role)

        await interaction.response.send_message(f"You have {roles} from Selected Menu", ephemeral=True)

    @discord.ui.button(label="Back To Menu", style=discord.ButtonStyle.red, emoji="🔙", custom_id="self_role_menu:game:return")
    async def self_role_return_game(self, button: discord.ui.View, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Select Your Menu from here", view=self_role_menu_main())

    @discord.ui.button(label="End Interaction", style=discord.ButtonStyle.red, emoji="<:pepeexit:790189030569934849>", custom_id="self_role_menu:bot:exit")
    async def self_role_end_bot(self, button: discord.ui.View, interaction: discord.Interaction):
        for button in self.children:
            button.disabled = True

        await interaction.response.edit_message(view=self)


class self_role_menu_server(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Announcement", style=discord.ButtonStyle.green, emoji="<a:tgk_announce:848804249525551134>", custom_id="self_role_menu:announcement")
    async def self_role_announcement(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        role = discord.utils.get(guild.roles, id=int(server_role[0]))
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Remvoed", ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Added", ephemeral=True)

    @discord.ui.button(label="Server Events", style=discord.ButtonStyle.green, emoji="<a:celebrateyay:821698856202141696>", custom_id="self_role_menu:server_events")
    async def self_role_server_events(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        role = discord.utils.get(guild.roles, id=int(server_role[1]))
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Remvoed", ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Added", ephemeral=True)

    @discord.ui.button(label="Server Polls", style=discord.ButtonStyle.green, emoji="<a:rainbowbirdupvote:804053833306210344>", custom_id="self_role_menu:server_polls")
    async def self_role_server_polls(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        role = discord.utils.get(guild.roles, id=int(server_role[2]))
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Remvoed", ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Added", ephemeral=True)

    @discord.ui.button(label="Casino Updates", style=discord.ButtonStyle.green, emoji="<a:TGK_slots:842628623571091457>", custom_id="self_role_menu:casino_updates")
    async def self_role_casino_updates(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        role = discord.utils.get(guild.roles, id=int(server_role[3]))
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Remvoed", ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Added", ephemeral=True)

    @discord.ui.button(label="Movie Night", style=discord.ButtonStyle.green, emoji="<a:tgk_movienight:842675039833030666>", custom_id="self_role_menu:movie_night")
    async def self_role_movie_night(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        role = discord.utils.get(guild.roles, id=int(server_role[4]))
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Remvoed", ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Added", ephemeral=True)

    @discord.ui.button(label="Check Roles", style=discord.ButtonStyle.blurple, emoji="<:TGK_check:851521037544062996>", custom_id="self_role_menu:server:check")
    async def self_role_check_server(self, button: discord.ui.View, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        has_role = []
        for ids in server_role:
            role = discord.utils.get(guild.roles, id=int(ids))
            if role in user.roles:
                has_role.append(role.mention)

        if len(has_role) == 0:
            roles = "None"
        else:
            roles = ",".join(has_role)

        await interaction.response.send_message(f"You have {roles} from Selected Menu", ephemeral=True)

    @discord.ui.button(label="Back To Menu", style=discord.ButtonStyle.red, emoji="🔙", custom_id="self_role_menu:game:return")
    async def self_role_return_game(self, button: discord.ui.View, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Select Your Menu from here", view=self_role_menu_main())

    @discord.ui.button(label="End Interaction", style=discord.ButtonStyle.red, emoji="<:pepeexit:790189030569934849>", custom_id="self_role_menu:server:exit")
    async def self_role_end_server(self, button: discord.ui.View, interaction: discord.Interaction):
        for button in self.children:
            button.disabled = True

        await interaction.response.edit_message(view=self)


class self_role_menu_giveaway(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Giveaways", style=discord.ButtonStyle.green, emoji="<a:tadaa:806631994770849843>", custom_id="self_role_menu:giveaways")
    async def self_role_giveaways(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        role = discord.utils.get(guild.roles, id=int(giveaways_roles[0]))
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Remvoed", ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Added", ephemeral=True)

    @discord.ui.button(label="Flash Giveaways", style=discord.ButtonStyle.green, emoji="<a:celebrate:817302382630273054>", custom_id="self_role_menu:flash_giveaways")
    async def self_role_flash_giveaways(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        role = discord.utils.get(guild.roles, id=int(giveaways_roles[1]))
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Remvoed", ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Added", ephemeral=True)

    @discord.ui.button(label="Other Giveaways", style=discord.ButtonStyle.green, emoji="<a:tgk_gift:820323551520358440>", custom_id="self_role_menu:other_giveaways")
    async def self_role_other_giveaways(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        role = discord.utils.get(guild.roles, id=int(giveaways_roles[2]))
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Remvoed", ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Added", ephemeral=True)

    @discord.ui.button(label="Check Roles", style=discord.ButtonStyle.blurple, emoji="<:TGK_check:851521037544062996>", custom_id="self_role_menu:give:check")
    async def self_role_check_give(self, button: discord.ui.View, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        has_role = []
        for ids in giveaways_roles:
            role = discord.utils.get(guild.roles, id=int(ids))
            if role in user.roles:
                has_role.append(role.mention)
        roles = ",".join(has_role)
        await interaction.response.send_message(f"You have {roles} from Selected Menu", ephemeral=True)

    @discord.ui.button(label="Back To Menu", style=discord.ButtonStyle.red, emoji="🔙", custom_id="self_role_menu:give:return")
    async def self_role_return_game(self, button: discord.ui.View, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Select Your Menu from here", view=self_role_menu_main())

    @discord.ui.button(label="End Interaction", style=discord.ButtonStyle.red, emoji="<:pepeexit:790189030569934849>", custom_id="self_role_menu:give:exit")
    async def self_role_end_give(self, button: discord.ui.View, interaction: discord.Interaction):
        for button in self.children:
            button.disabled = True

        await interaction.response.edit_message(view=self)


class self_role_menu_partner(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Partnership', style=discord.ButtonStyle.green, emoji="<a:pandanod:809461710879588384>", custom_id="self_role_menu:partnership")
    async def self_role_partnership(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        role = discord.utils.get(guild.roles, id=int(partnership_roles[0]))
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Remvoed", ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Added", ephemeral=True)

    @discord.ui.button(label='No Partnership', style=discord.ButtonStyle.green, emoji="<a:bunnyno:809007055230074930>", custom_id="self_role_menu:no_partnership")
    async def self_role_no_partnership(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        role = discord.utils.get(guild.roles, id=int(partnership_roles[1]))
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Remvoed", ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Added", ephemeral=True)

    @discord.ui.button(label="Check Roles", style=discord.ButtonStyle.blurple, emoji="<:TGK_check:851521037544062996>", custom_id="self_role_menu:check")
    async def self_role_check_parnter(self, button: discord.ui.View, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        has_role = []
        for ids in partnership_roles:
            role = discord.utils.get(guild.roles, id=int(ids))
            if role in user.roles:
                has_role.append(role.mention)

        if len(has_role) == 0:
            roles = "None"
        else:
            roles = ",".join(has_role)

        await interaction.response.send_message(f"You have {roles} from Selected Menu", ephemeral=True)

    @discord.ui.button(label="Back To Menu", style=discord.ButtonStyle.red, emoji="🔙", custom_id="self_role_menu:game:return")
    async def self_role_return_game(self, button: discord.ui.View, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Select Your Menu from here", view=self_role_menu_main())

    @discord.ui.button(label="End Interaction", style=discord.ButtonStyle.red, emoji="<:pepeexit:790189030569934849>", custom_id="self_role_menu:partnership:exit")
    async def self_role_end_give(self, button: discord.ui.View, interaction: discord.Interaction):
        for button in self.children:
            button.disabled = True

        await interaction.response.edit_message(view=self)


class self_role_menu_dank(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Heists", style=discord.ButtonStyle.green, emoji="<a:flymoney:803336135803404301>", custom_id="self_role_menu:heists")
    async def self_role_heists(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        role = discord.utils.get(guild.roles, id=int(dank_roles[0]))
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Remvoed", ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Added", ephemeral=True)

    @discord.ui.button(label="Partner Heists", style=discord.ButtonStyle.green, emoji="<a:peperobber:804070327344562217>", custom_id="self_role_menu:partner_heists")
    async def self_role_partner_heists(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        role = discord.utils.get(guild.roles, id=int(dank_roles[1]))
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Remvoed", ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Added", ephemeral=True)

    @discord.ui.button(label="Outside Heists", style=discord.ButtonStyle.green, emoji="<a:bhaago:821993760492879872>", custom_id="self_role_menu:outside_heists")
    async def self_role_outside_heists(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        role = discord.utils.get(guild.roles, id=int(dank_roles[2]))
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Remvoed", ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Added", ephemeral=True)

    @discord.ui.button(label="Shopper's Delight", style=discord.ButtonStyle.green, emoji="<a:yippeeee:804392376441110598>", custom_id="self_role_menu:shopper_delight")
    async def self_role_shopper_delight(self, button: discord.ui.Button, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        role = discord.utils.get(guild.roles, id=int(dank_roles[3]))
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Remvoed", ephemeral=True)
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"{role.mention} Has Added", ephemeral=True)

    @discord.ui.button(label="Check Roles", style=discord.ButtonStyle.blurple, emoji="<:TGK_check:851521037544062996>", custom_id="self_role_menu:dank:check")
    async def self_role_check_dank(self, button: discord.ui.View, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        has_role = []
        for ids in dank_roles:
            role = discord.utils.get(guild.roles, id=int(ids))
            if role in user.roles:
                has_role.append(role.mention)

        if len(has_role) == 0:
            roles = "None"
        else:
            roles = ",".join(has_role)

        await interaction.response.send_message(f"You have {roles} from Selected Menu", ephemeral=True)

    @discord.ui.button(label="Back To Menu", style=discord.ButtonStyle.red, emoji="🔙", custom_id="self_role_menu:game:return")
    async def self_role_return_game(self, button: discord.ui.View, interaction: discord.Interaction):
        await interaction.response.edit_message(content="Select Your Menu from here", view=self_role_menu_main())

    @discord.ui.button(label="End Interaction", style=discord.ButtonStyle.red, emoji="<:pepeexit:790189030569934849>", custom_id="self_role_menu:dank:exit")
    async def self_role_end_dank(self, button: discord.ui.View, interaction: discord.Interaction):
        for button in self.children:
            button.disabled = True

        await interaction.response.edit_message(view=self)


class self_role_menu_main(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(placeholder="Select your Role Menu from here", max_values=1, custom_id="self_role_menu_main:min",
                       options=[
                           discord.SelectOption(
                               label="Game Pings", value=0, emoji="<a:rarepepe:801693036911263744>"),
                           discord.SelectOption(
                               label="Bot Roles", value=1, emoji="🤖"),
                           discord.SelectOption(
                               label="Server Pings", value=2, emoji="📣"),
                           discord.SelectOption(
                               label="Giveaway", value=3, emoji="🎉"),
                           discord.SelectOption(
                               label="Partnership Program", value=4, emoji="🤝"),
                           discord.SelectOption(
                               label="Dank Pings", value=5, emoji="<a:peperobber:804070327344562217>"),
                       ])
    async def self_role_main(self, select: discord.ui.Select, interaction: discord.Interaction):
        menu = int(select.values[0])
        if menu == 0:
            await interaction.response.edit_message(content="Here is your Role menu", view=(self_role_menu_game()))
        if menu == 1:
            await interaction.response.edit_message(content="Here is your Role menu", view=(self_role_menu_bot()))
        if menu == 2:
            await interaction.response.edit_message(content="Here is your Role menu", view=(self_role_menu_server()))
        if menu == 3:
            await interaction.response.edit_message(content="Here is your Role menu", view=(self_role_menu_giveaway()))
        if menu == 4:
            await interaction.response.edit_message(content="Here is your Role menu", view=(self_role_menu_partner()))
        if menu == 5:
            await interaction.response.edit_message(content="Here is your Role menu", view=(self_role_menu_dank()))


class self_role_menu_main_start(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Click Me To Start", style=discord.ButtonStyle.blurple, custom_id="self_role_menu:start")
    async def self_role_start(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message('You Can start customizing your roles by select and option from below message', view=self_role_menu_main(), ephemeral=True)


class self_role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(self_role_menu_main())
        self.bot.add_view(self_role_menu_game())
        self.bot.add_view(self_role_menu_server())
        self.bot.add_view(self_role_menu_giveaway())
        self.bot.add_view(self_role_menu_partner())
        self.bot.add_view(self_role_menu_dank())
        print(f"{self.__class__.__name__} Is Ready")

    @commands.command()
    @commands.is_owner()
    async def selfrole(self, ctx):
        embed = discord.Embed(title="Self Roles", color=0x9e3bff,
                              description="Use the below dropdown menu to select your roles")
        embed.set_footer(
            text=f"{ctx.guild.name}", icon_url="https://cdn.discordapp.com/icons/785839283847954433/a_23007c59f65faade4c973506d9e66224.gif?size=1024")
        embed.timestamp = datetime.datetime.utcnow()
        await ctx.send(embed=embed, view=self_role_menu_main_start())


def setup(bot):
    bot.add_cog(self_role(bot))

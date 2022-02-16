from discord.ext import commands
import discord
import asyncio
from utils.checks import checks
from utils.util import Pag


class Main_panel(discord.ui.View):
    def __init__(self, bot, ctx, message: discord.Message):
        super().__init__(timeout=10)
        self.bot = bot
        self.ctx = ctx
        self.message = message
    
    @discord.ui.button(label="Title", style=discord.ButtonStyle.blurple)
    async def title(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        title_m = await interaction.message.reply(f"{interaction.user.mention}, Enter Title for embed")
        await interaction.message.edit(view=None)

        try:
            title = await self.bot.wait_for('message', check=lambda m: m.author == self.ctx.author)
        except asyncio.TimeoutError:
            await interaction.message.edit(view=Main_panel(self.bot, self.ctx, self.message))
            await interaction.followup.send("Timed out, Try Again", ephemeral=True)
            return

        embed = self.message.embeds[0]
        embed.title = title.content
        await title.delete()
        await title_m.delete()
        await self.message.edit(embed=embed)
        await interaction.message.edit(view=Main_panel(self.bot, self.ctx, self.message))
        await interaction.followup.send("Updated", ephemeral=True)

    @discord.ui.button(label="Description", style=discord.ButtonStyle.blurple)
    async def description(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        description_m = await interaction.message.reply(f"{interaction.user.mention}, Enter Description for embed")
        await interaction.message.edit(view=None)

        try:
            description = await self.bot.wait_for('message', check=lambda m: m.author == self.ctx.author)
        except asyncio.TimeoutError:
            await interaction.message.edit(view=Main_panel(self.bot, self.ctx, self.message))
            await interaction.followup.send("Timed out, Try Again", ephemeral=True)
            return

        embed = self.message.embeds[0]
        embed.description = description.content
        await description.delete()
        await description_m.delete()
        await self.message.edit(embed=embed)
        await interaction.message.edit(view=Main_panel(self.bot, self.ctx, self.message))
        await interaction.followup.send("Updated", ephemeral=True)
        
    
    @discord.ui.button(label="Color", style=discord.ButtonStyle.blurple)
    async def color(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        color_m = await interaction.message.reply(f"{interaction.user.mention}, Enter Color for embed")
        await interaction.message.edit(view=None)

        try:
            color = await self.bot.wait_for('message', check=lambda m: m.author == self.ctx.author)
        except asyncio.TimeoutError:
            await interaction.message.edit(view=Main_panel(self.bot, self.ctx, self.message))
            await interaction.followup.send("Timed out, Try Again", ephemeral=True)
            return

        embed = self.message.embeds[0]
        embed.color = int(color.content, 16)
        await color.delete()
        await color_m.delete()
        await self.message.edit(embed=embed)
        await interaction.message.edit(view=Main_panel(self.bot, self.ctx, self.message))
        await interaction.followup.send("Updated", ephemeral=True)

    @discord.ui.button(label="Thumbnail", style=discord.ButtonStyle.blurple)
    async def thumbnail(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        thumbnail_m = await interaction.message.reply(f"{interaction.user.mention}, Enter Thumbnail url for embed, send none to remove thumbnail")
        await interaction.message.edit(view=None)

        try:
            thumbnail = await self.bot.wait_for('message', check=lambda m: m.author == self.ctx.author)
        except asyncio.TimeoutError:
            await interaction.message.edit(view=Main_panel(self.bot, self.ctx, self.message))
            await interaction.followup.send("Timed out, Try Again", ephemeral=True)
            return
        
        embed = self.message.embeds[0]
        if thumbnail.content == "none" or thumbnail.content == "None":
            embed.set_thumbnail(url=discord.Embed.Empty)
        else:
            embed.set_thumbnail(url=thumbnail.content)
        await thumbnail.delete()
        await thumbnail_m.delete()
        await self.message.edit(embed=embed)
        await interaction.message.edit(view=Main_panel(self.bot, self.ctx, self.message))
        await interaction.followup.send("Updated", ephemeral=True)
    
    @discord.ui.button(label="Buttons", style=discord.ButtonStyle.green, emoji="🔗")
    async def buttons(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(view=Button_Panel(self.bot, self.ctx, self.message))

    # # @discord.ui.button(label="Field", style=discord.ButtonStyle.blurple)
    # # async def Field(self, button: discord.ui.Button, interaction: discord.Interaction):
    # #     await interaction.response.edit_message(view=Field_Maker(self.bot, self.ctx, self.message))
    
    # # @discord.ui.button(label="Footer", style=discord.ButtonStyle.blurple)
    # # async def footer(self, button: discord.ui.Button, interaction: discord.Interaction):
    # #     await interaction.response.edit_message(view=Footer_maker(self.bot, self.ctx))
    
    async def on_interaction(self, interaction):
        if interaction.user.id == self.ctx.author.id:
            return True
        else:
            await interaction.response.send_message("You can't edit this embed", ephemeral=True)

class Button_Panel(discord.ui.View):
    def __init__(self, bot, ctx, message: discord.Message):
        super().__init__(timeout=10)
        self.bot = bot
        self.ctx = ctx
        self.message = message
    
    @discord.ui.button(label="Add Button", style=discord.ButtonStyle.blurple)
    async def add_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        button_m = await interaction.message.reply(f"Enter Count of Total Button")
        total_button = await self.bot.wait_for('message', check=lambda m: m.author == self.ctx.author)

        view = discord.ui.View.from_message(self.message)

        for i in range(int(total_button.content)):

            await button_m.edit(f"{interaction.user.mention}, Enter Button Label for Button, Enter Stop to stop")
            await interaction.message.edit(view=None)
            if button_m.content.lower() == "stop":
                await button_m.delete()
                await total_button.delete
                
                break
            try:
                button_text = await self.bot.wait_for('message', check=lambda m: m.author == self.ctx.author)
                await button_m.edit(f"{interaction.user.mention}, Enter Button URL for Button")
                button_link = await self.bot.wait_for('message', check=lambda m: m.author == self.ctx.author)
            except asyncio.TimeoutError:
                await interaction.message.edit(view=Button_Panel(self.bot, self.ctx, self.message))
                await interaction.followup.send("Timed out, Try Again", ephemeral=True)
                return
            
            view.add_item(discord.ui.Button(label=button_text.content, url=button_link.content))
            await button_text.delete()
            await button_link.delete()


        await interaction.message.edit(view=None)
        await button_m.delete()
        
        await self.message.edit(view=view)
        await interaction.message.edit(view=self)
        await interaction.followup.send("Updated", ephemeral=True)

    @discord.ui.button(label="Remove Button", style=discord.ButtonStyle.red)
    async def remove_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        button_m = await interaction.message.reply(f"{interaction.user.mention}, Enter Button Index of button to remove, Remember index start from 0")
        await interaction.message.edit(view=None)

        try:

            button_index = await self.bot.wait_for('message', check=lambda m: m.author == self.ctx.author)

        except asyncio.TimeoutError:

            await interaction.message.edit(view=Button_Panel(self.bot, self.ctx, self.message))
            await interaction.followup.send("Timed out, Try Again", ephemeral=True)
            return
        
        view = discord.ui.View.from_message(self.message)
        view.remove_item(int(button_index.content))
        await button_index.delete()
        await button_m.delete()
        await self.message.edit(view=view)
        await interaction.message.edit(view=Main_panel(self.bot, self.ctx, self.message))

    @discord.ui.button(label="Back", style=discord.ButtonStyle.red)
    async def back(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(view=Main_panel(self.bot, self.ctx, self.message))

# class Footer_maker(discord.ui.View):
#     def __init__(self, bot, ctx):
#         super().__init__(timeout=60)
#         self.bot = bot
#         self.ctx = ctx
    
#     @discord.ui.button(label="Text", style=discord.ButtonStyle.blurple)
#     async def text(self, button: discord.ui.Button, interaction: discord.Interaction):
#         await interaction.response.defer(ephemeral=True)
#         await interaction.message.edit(view=None)
#         text_m = await self.ctx.send("Send Embed Footer Text")
#         text = await self.bot.wait_for('message', check=lambda m: m.author == self.ctx.author)
#         embed = interaction.message.embeds[0]
#         embed.set_footer(text=text.content)
#         await text.delete()
#         await text_m.delete()
#         await interaction.message.edit(embed=embed, view=self)
    
#     @discord.ui.button(label="Icon", style=discord.ButtonStyle.blurple)
#     async def icon(self, button: discord.ui.Button, interaction: discord.Interaction):
#         await interaction.response.defer(ephemeral=True)
#         await interaction.message.edit(view=None)
#         icon_m = await self.ctx.send("Send Embed Footer Icon")
#         icon = await self.bot.wait_for('message', check=lambda m: m.author == self.ctx.author)
#         embed = interaction.message.embeds[0]
#         embed.footer.icon_url = icon.content
#         await icon.delete()
#         await icon_m.delete()
#         await interaction.message.edit(embed=embed, view=self)
    
#     @discord.ui.button(label="Back", style=discord.ButtonStyle.blurple)
#     async def back(self, button: discord.ui.Button, interaction: discord.Interaction):
#         await interaction.response.edit_message(view=Main_panel(self.bot, self.ctx))
    
#     async def on_interaction(self, interaction):
#         if interaction.user.id == self.ctx.author.id:
#             return True
#         else:
#             await interaction.response.send_message("You can't edit this embed", ephemeral=True)


# class Field_Maker(discord.ui.View):
#     def __init__(self, bot, ctx):
#         super().__init__(timeout=60)
#         self.bot = bot
#         self.ctx = ctx
    
#     @discord.ui.button(label="Add Field", style=discord.ButtonStyle.blurple)
#     async def name(self, button: discord.ui.Button, interaction: discord.Interaction):
#         await interaction.response.defer(ephemeral=True)
#         await interaction.message.edit(view=None)
#         name_m = await self.ctx.send("Send Embed Field Name")
#         name = await self.bot.wait_for('message', check=lambda m: m.author == self.ctx.author)
#         await name_m.edit("Enter Feild Value")
#         value = await self.bot.wait_for('message', check=lambda m: m.author == self.ctx.author)
#         await name_m.edit("Enter Feild Inline (Yes/No)")
#         inline_m = await self.bot.wait_for('message', check=lambda m: m.author == self.ctx.author)
#         if inline_m.content.lower() == "yes" or 'y':
#             inline = True
#         else:
#             inline = False
#         embed = interaction.message.embeds[0]
#         embed.add_field(name=name.content, value=value.content, inline=inline)
        
#         await name.delete()
#         await value.delete()
#         await inline_m.delete()
#         await name_m.delete()
#         await interaction.message.edit(embed=embed, view=self)

#     @discord.ui.button(label="Add Field At Index", style=discord.ButtonStyle.blurple)
#     async def index(self, button: discord.ui.Button, interaction: discord.Interaction):
#         await interaction.response.defer(ephemeral=True)
#         await interaction.message.edit(view=None)
#         index_m = await self.ctx.send("Enter Index of Field\n Indext starts at from 0")
#         index = await self.bot.wait_for('message', check=lambda m: m.author == self.ctx.author)
#         await index_m.edit("Enter Feild Name")
#         name = await self.bot.wait_for('message', check=lambda m: m.author == self.ctx.author)
#         await index_m.edit("Enter Feild Value")
#         value = await self.bot.wait_for('message', check=lambda m: m.author == self.ctx.author)
#         await index_m.edit("Enter Feild Inline (Yes/No)")
#         inline_m = await self.bot.wait_for('message', check=lambda m: m.author == self.ctx.author)
#         if inline_m.content.lower() == "yes" or 'y':
#             inline = True
#         else:
#             inline = False
#         embed = interaction.message.embeds[0]
#         embed.add_field(name=name.content, value=value.content, inline=inline, at=int(index.content))
        
#         await name.delete()
#         await value.delete()
#         await inline_m.delete()
#         await index_m.delete()
#         await interaction.message.edit(embed=embed, view=self)
    
#     @discord.ui.button(label="Clear Field", style=discord.ButtonStyle.blurple)
#     async def clear(self, button: discord.ui.Button, interaction: discord.Interaction):
#         await interaction.response.defer(ephemeral=True)
#         await interaction.message.edit(view=None)
#         embed = interaction.message.embeds[0]
#         embed.clear_fields()
#         await interaction.message.edit(embed=embed, view=self)
        
#     @discord.ui.button(label="Back", style=discord.ButtonStyle.green)
#     async def back(self, button: discord.ui.Button, interaction: discord.Interaction):
#         await interaction.response.edit_message(view=Main_panel(self.bot, self.ctx))

class Save_embed(discord.ui.View):
    def __init__(self, ctx, bot,embed_name,data,button_data=None):
        super().__init__()
        self.ctx = ctx
        self.data = data
        self.bot = bot
        self.embed_name = embed_name
        self.button_data = button_data
    
    #make an button name Save Embed by using discord.ui.button decorator
    @discord.ui.button(label="Save Embed", style=discord.ButtonStyle.blurple)
    async def save_embed(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        embed_filter = {'guild_id': self.ctx.guild.id,'created_by': self.ctx.author.id, 'Key_name': self.embed_name}
        embed_data = {'embed': self.data, 'button_data': self.button_data}
        await self.bot.embeds.upsert_custom(embed_filter, embed_data)

        await interaction.followup.send("Embed saved!",ephemeral=True)
        for button in self.children:
            button.disabled = True
        await interaction.message.edit(view=self)

    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.user.id == self.ctx.author.id:            
            return True
        else:
            interaction.response.send_message("you didn't invoke this command", ephemeral=True)

class Embeds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} Cog has been loaded\n-----")
    
    @commands.group(name="Embed",description="Send Embed by it's Key Name",invoke_without_command=True)
    @commands.check_any(checks.can_use())
    async def embed(self, ctx, *,key_name:str):
        await ctx.message.delete()
        embed_filter = {'guild_id': ctx.guild.id,'Key_name': key_name}
        embed_data = await self.bot.embeds.find_by_custom(embed_filter)
        if not embed_data:
            await ctx.send("Embed not found")
            return
        embed = embed_data['embed']
        button = embed_data['button_data']    
        if button:
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label=button['button_label'], url=button['button_url']))
            await ctx.send(embed=discord.Embed().from_dict(embed), view=view)
        else:
            await ctx.send(embed=discord.Embed().from_dict(embed))
        
    @embed.command(name="create", description="create an nice good looking Embed")
    @commands.check_any(checks.can_use())
    async def create(self, ctx):
        data = {'type': 'rich'}
        button_data = {}
        preview_embed = discord.Embed(title="This is a Preview Embed", description="This is a Preview Embed", color=0xE74C3C)
        preview_message = await ctx.send(embed=preview_embed)
        control_embed = discord.Embed(description="Select your Option from below Buttons to customize your embed", color=self.bot.user.color)
        control_embed.set_footer(text=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=control_embed, view=Main_panel(self.bot, ctx, preview_message))
        # try:
        
        #     qestion_messge = await ctx.send("Send name of Embed which will be use to send embed later")
        #     embed_name = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=120)            
        #     embed_name = embed_name.content
        #     check_name = await self.bot.embeds.find_by_custom({"Key_name": embed_name})

        #     if check_name is None:
        #         pass
        #     else:
        #         return await ctx.send("Embed with this name already exist")
        #     await qestion_messge.edit(content="Send title of Embed")
        #     title = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel,timeout=120)
        #     data['title'] = title.content
        #     await preview_message.edit(embed=discord.Embed().from_dict(data))
        #     await title.delete()

        #     await qestion_messge.edit("Send color Hex for Embed")
        #     color = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel,timeout=120)
        #     data['color'] = int(color.content, base=16)
        #     await preview_message.edit(embed=discord.Embed().from_dict(data))
        #     await color.delete()

        #     await qestion_messge.edit("Send description for Embed")
        #     description = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel,timeout=120)
        #     data['description'] = description.content
        #     await preview_message.edit(embed=discord.Embed().from_dict(data))
        #     await description.delete()

        #     await qestion_messge.edit("Send url for Embed, Send None if you don't want to add a url")
        #     url = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel,timeout=120)
        #     if url.content.lower() == "none":
        #         pass
        #     else:
        #         data['thumbnail'] = {'url': url.content}
        #     await preview_message.edit(embed=discord.Embed().from_dict(data))
        #     await url.delete()

        #     await qestion_messge.edit("if You want to add Link button to message send 'Yes' else send 'No'")
        #     confrim = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel,timeout=120)

        #     if confrim.content.lower() == "yes" or 'y':
        #         await confrim.delete()
        #         await qestion_messge.edit("Send Button lable")
        #         button_name = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel,timeout=120)
        #         button_data['button_label'] =  button_name.content
        #         await button_name.delete()
        #         await qestion_messge.edit("Send Button url")
        #         button_url = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel,timeout=120)
        #         button_data['button_url'] = button_url.content
        #         await button_url.delete()
        #         view = discord.ui.View()
        #         view.add_item(discord.ui.Button(label=button_data['button_label'], url=button_data['button_url']))
        #         await preview_message.edit(view=view)

        #     await qestion_messge.delete()

        #     await preview_message.reply("Do you want to Save This Emebed", view=Save_embed(ctx, self.bot, embed_name,data,button_data))

        # except asyncio.TimeoutError:
        #     return await ctx.send("TimeoutError")
    
    @embed.command(name="restart", description="Edit an Embed")
    #@commands.check_any(checks.can_use())
    async def restart(self, ctx, *,id:int):
        try:
            message = await ctx.channel.fetch_message(id)
        except discord.NotFound:
            return await ctx.send("Message not found")
        
        await ctx.message.delete()
        await message.edit(view=None)
        embed = message.embeds[0]
        preview_message = await ctx.send(embed=embed)
        control_embed = discord.Embed(description="Select your Option from below Buttons to customize your embed", color=self.bot.user.color)
        control_embed.set_footer(text=f"{ctx.author.name}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=control_embed,view=Main_panel(self.bot, ctx, preview_message))
        

    @embed.command(name="steal", description="Steal Embed from any Message")
    @commands.check_any(checks.can_use())
    async def steal(self, ctx, channel: discord.TextChannel, id: int):
        message = await channel.fetch_message(id)
        if len(message.embeds) == 0:
            return await ctx.send("This message not have embed")        
        else:
            embed = message.embeds[0].to_dict()

            await ctx.send("This is Preview Embed", embed=discord.Embed().from_dict(embed))
            try:
                qestion_messge = await ctx.send("Do you want to Save This Emebed (Yes/No)")
                ans = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author and m.channel == ctx.channel,timeout=120)
                if ans.content.lower() == "yes" or 'y':
                    qestion_messge = await ctx.send("Send name of Embed which will be use to send embed later")
                    embed_name = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author, timeout=120)
                    embed_name = embed_name.content
                    check_name = await self.bot.embeds.find_by_custom({"Key_name": embed_name})

                    if check_name:
                        return await ctx.send("Embed with this name already exist")
                    
                    await qestion_messge.edit(view=Save_embed(ctx, self.bot,embed_name ,embed))
                else:
                    return
            except asyncio.TimeoutError:
                return await ctx.send("TimeoutError")

def setup(bot):
    bot.add_cog(Embeds(bot))

"""
MIT License

Copyright (c) 2022 Marseel-E

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

__all__ = ['Paginator']


from discord import Interaction, SelectOption, User, ButtonStyle
from discord.ui import View, select, Select, button, Button
from typing import Optional, List, Union
from discord.ext import commands

class _select(Select):
	def __init__(self, pages: List[str]):
		super().__init__(placeholder="Quick navigation", min_values=1, max_values=1, options=pages, row=0)


	async def callback(self, interaction: Interaction):
		self.view.current_page = int(self.values[0])

		await self.view.update_children(interaction)


class _view(View):
	def __init__(self, author: User, pages: List[SelectOption], embeded: bool):
		super().__init__(timeout=15)
		self.author = author
		self.pages = pages
		self.embeded = embeded

		self.current_page = 0

	async def interaction_check(self, interaction: Interaction) -> bool:
		return (interaction.user.id == self.author.id)

	async def on_timeout(self):		
		self.stop()

	async def update_children(self, interaction: Interaction):
		self.next.disabled = (self.current_page + 1 == len(self.pages))
		self.previous.disabled = (self.current_page <= 0)
		self.last.disabled=self.next.disabled
		self.first.disabled=self.previous.disabled

		kwargs = {'content': self.pages[self.current_page]} if not (self.embeded) else {'embed': self.pages[self.current_page]}
		kwargs['view'] = self

		await interaction.response.edit_message(**kwargs)


	@button(label="<<", style=ButtonStyle.gray, row=1)
	async def first(self, interaction: Interaction, button: Button):
		self.current_page = 0

		await self.update_children(interaction)

	@button(label="<", style=ButtonStyle.gray, row=1)
	async def previous(self, interaction: Interaction, button: Button):
		self.current_page -= 1

		await self.update_children(interaction)

	
	@button(label="◼", style=ButtonStyle.gray, row=1,custom_id='stop')
	async def quit(self, interaction: Interaction, button: Button):
		kwargs = {'content': self.pages[self.current_page]} if not (self.embeded) else {'embed': self.pages[self.current_page]}

		for button in self.children:
			button.disabled = True

		kwargs['view'] = self
		
		await interaction.response.edit_message(**kwargs)
		self.stop()

	@button(label=">", style=ButtonStyle.gray, row=1)
	async def next(self, interaction: Interaction, button: Button):
		self.current_page += 1

		await self.update_children(interaction)

	@button(label=">>", style=ButtonStyle.gray, row=1)
	async def last(self, interaction: Interaction, button: Button):
		self.current_page = len(self.pages) - 1

		await self.update_children(interaction)

class Paginator:
	def __init__(self, interaction: Interaction, pages: list, custom_children: Optional[List[Union[Button, Select]]] = []):
		self.custom_children = custom_children
		self.interaction = interaction
		self.pages = pages


	async def start(self, embeded: Optional[bool] = False, quick_navigation: bool = True) -> None:
		"""Starts the paginator.

		Parameters
		-----------
			'embeded' - Whether the pages are embeds or just text.
			'quick_navigation' - Whether to include quick naviagtion or not.

		Raises
		-------
			'Missing pages' - an empty list was passed to 'pages'.
		"""
		if not (self.pages): raise ValueError("Missing pages")

		view = _view(self.interaction.user, self.pages, embeded)

		if (len(self.custom_children) == 5):
			for index,button in enumerate(view.children):
				button.style = self.custom_children[index].style
				button.url = self.custom_children[index].url
				button.label = self.custom_children[index].label
				button.emoji = self.custom_children[index].emoji
				button.row = self.custom_children[index].row
				button.disabled = self.custom_children[index].disabled
		elif (len(self.custom_children) == 4):
			view.remove_item(view.quit)
			for index,button in enumerate(view.children):
				button.style = self.custom_children[index].style
				button.url = self.custom_children[index].url
				button.label = self.custom_children[index].label
				button.emoji = self.custom_children[index].emoji
				button.row = self.custom_children[index].row
				button.disabled = self.custom_children[index].disabled
		elif (len(self.custom_children) == 3):
			view.remove_item(view.first)
			view.remove_item(view.last)
			for index,button in enumerate(view.children):
				button.style = self.custom_children[index].style
				button.url = self.custom_children[index].url
				button.label = self.custom_children[index].label
				button.emoji = self.custom_children[index].emoji
				button.row = self.custom_children[index].row
				button.disabled = self.custom_children[index].disabled

		view.previous.disabled = True if (view.current_page <= 0) else False
		view.next.disabled = True if (view.current_page + 1 >= len(self.pages)) else False
		view.last.disabled=view.next.disabled
		view.first.disabled=view.previous.disabled

		if (quick_navigation):
			options = []
			for index, page in enumerate(self.pages):
				options.append(SelectOption(label=f"Page {index+1}", value=index))

			view.add_item(_select(options))

		kwargs = {'content': self.pages[view.current_page]} if not (embeded) else {'embed': self.pages[view.current_page]}
		kwargs['view'] = view

		await self.interaction.response.send_message(**kwargs)

		await view.wait()

		for button in view.children:
			button.disabled = True
		await self.interaction.edit_original_response(view=view)

class Contex_Paginator:
	def __init__(self, interaction: commands.Context, pages: list, custom_children: Optional[List[Union[Button, Select]]] = []):
		self.custom_children = custom_children
		self.interaction = interaction
		self.pages = pages


	async def start(self, embeded: Optional[bool] = False, quick_navigation: bool = True) -> None:
		"""Starts the paginator.

		Parameters
		-----------
			'embeded' - Whether the pages are embeds or just text.
			'quick_navigation' - Whether to include quick naviagtion or not.

		Raises
		-------
			'Missing pages' - an empty list was passed to 'pages'.
		"""
		if not (self.pages): raise ValueError("Missing pages")

		view = _view(self.interaction.author, self.pages, embeded)

		if (len(self.custom_children) == 5):
			for index,button in enumerate(view.children):
				button.style = self.custom_children[index].style
				button.url = self.custom_children[index].url
				button.label = self.custom_children[index].label
				button.emoji = self.custom_children[index].emoji
				button.row = self.custom_children[index].row
				button.disabled = self.custom_children[index].disabled
		elif (len(self.custom_children) == 4):
			view.remove_item(view.quit)
			for index,button in enumerate(view.children):
				button.style = self.custom_children[index].style
				button.url = self.custom_children[index].url
				button.label = self.custom_children[index].label
				button.emoji = self.custom_children[index].emoji
				button.row = self.custom_children[index].row
				button.disabled = self.custom_children[index].disabled
		elif (len(self.custom_children) == 3):
			view.remove_item(view.first)
			view.remove_item(view.last)
			for index,button in enumerate(view.children):
				button.style = self.custom_children[index].style
				button.url = self.custom_children[index].url
				button.label = self.custom_children[index].label
				button.emoji = self.custom_children[index].emoji
				button.row = self.custom_children[index].row
				button.disabled = self.custom_children[index].disabled

		view.previous.disabled = True if (view.current_page <= 0) else False
		view.next.disabled = True if (view.current_page + 1 >= len(self.pages)) else False
		view.last.disabled=view.next.disabled
		view.first.disabled=view.previous.disabled

		if (quick_navigation):
			options = []
			for index, page in enumerate(self.pages):
				options.append(SelectOption(label=f"Page {index+1}", value=index))

			view.add_item(_select(options))

		kwargs = {'content': self.pages[view.current_page]} if not (embeded) else {'embed': self.pages[view.current_page]}
		kwargs['view'] = view

		await self.interaction.channel.send(**kwargs)

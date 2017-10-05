import asyncio


class Paginator:

    def __init__(self, bot, ctx):
        self.bot = bot
        self.ctx = ctx
        self.embeds = []
        self.current_page = 0
        self.message = None
        self.action = None
        self.paginating = False
        self.reaction_emojis = [
            ('\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}', self.first_page),
            ('\N{BLACK LEFT-POINTING TRIANGLE}', self.previous_page),
            ('\N{BLACK RIGHT-POINTING TRIANGLE}', self.next_page),
            ('\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}', self.last_page)]

    def add_embed(self, embed):
        self.embeds.append(embed)

    async def first_page(self):
        await self.show_page(0)

    async def last_page(self):
        await self.show_page(len(self.embeds) - 1)

    async def first_page(self):
        await self.show_page(0)

    async def next_page(self):
        if self.current_page < len(self.embeds) - 1:
            await self.show_page(self.current_page + 1)

    async def previous_page(self):
        if self.current_page != 0:
            await self.show_page(self.current_page - 1)

    async def show_page(self, page_num):
        """Display the given page"""
        if self.paginating and page_num == self.current_page:
            return

        if len(self.embeds) == 0:
            return

        self.current_page = page_num

        if not self.message:
            self.message = await self.ctx.send(embed=self.embeds[self.current_page])
            await self.add_reactions()
        else:
            await self.message.edit(embed=self.embeds[self.current_page])

    def react_check(self, reaction, user):
        """Check if reaction is valid. Set action function if it matches"""
        if user is None or user.id != self.ctx.author.id:
            return False

        if reaction.message.id != self.message.id:
            return False

        for (emoji, func) in self.reaction_emojis:
            if reaction.emoji == emoji:
                self.action = func
                return True
        return False

    async def add_reactions(self):
        """Add reaction 'buttons'"""
        if len(self.embeds) == 1:
            return

        for (reaction, _) in self.reaction_emojis:
            if len(self.embeds) == 2 and reaction in ('\u23ed', '\u23ee'):
                continue
            await self.message.add_reaction(reaction)

    async def paginate(self):
        """Display message and start listening for reactions"""
        await self.show_page(self.current_page)
        self.paginating = True

        while self.paginating:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=self.react_check, timeout=120.0)
            except asyncio.TimeoutError:
                self.paginating = False
                try:
                    await self.message.clear_reactions()
                except:
                    pass
                finally:
                    break

            try:
                await self.message.remove_reaction(reaction, user)
            except:
                pass

            await self.action()

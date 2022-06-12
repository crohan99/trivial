import requests

from random import randint
from twitchio.ext import commands

class Bot(commands.Bot):

    curUser = ''
    curPrompt = ''
    curAnswer = ''
    curIncorrect = {}

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(token='zj3nhpbiun93gav6e4lth774qum4ql', prefix='!', initial_channels=['motorslam99'])

    async def event_ready(self):
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message):
        # Messages with echo set to True are messages sent by the bot...
        # For now we just want to ignore them...
        if message.echo:
            return

        # Print the contents of our message to console...
        print(message.content)

        # Since we have commands and are overriding the default `event_message`
        # We must let the bot know we want to handle and invoke our commands...
        await self.handle_commands(message)

    @commands.command(name = 'trivia')
    async def twitch_command(self, ctx: commands.Context):
        self.curUser = ctx.author.name

        # get trivia prompts
        self.getPrompts()
        await self.promptUser(ctx)
        # await ctx.send(f'Hello!')

    def getPrompts(self):
        URL = 'https://opentdb.com/api.php?amount=10'
        PARAMS = {'prompt':'answer'}

        rand = randint(0, 10)
        r = requests.get(url = URL, params = PARAMS)
        data = r.json()

        print(data['results'][rand]['question'])
        self.curPrompt = data['results'][rand]['question']
        self.curAnswer = data['results'][rand]['correct_answer']
        self.curIncorrect = data['results'][rand]['incorrect_answers']

    async def promptUser(self, ctx):
        await ctx.send(f'Here is your question, {self.curUser}: \n {self.curPrompt} \n')

bot = Bot()
bot.run()
import requests

from random import randint
from twitchio.ext import commands

TRIVIA_API_URL = 'https://opentdb.com/api.php?amount=10'
TRIVIA_API_PARAMS = {'prompt':'answer'}

class Bot(commands.Bot):
    user = ''
    prompt = ''
    answer = ''
    incorrect_answers = {}
    trivia_started = False
    options = {0: 'a',
               1: 'b',
               2: 'c',
               3: 'd'}

    def __init__(self):
        # init bot
        super().__init__(token='zj3nhpbiun93gav6e4lth774qum4ql', prefix='!', initial_channels=['motorslam99'])

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    async def event_message(self, message, ctx: commands.Context):
        # Messages with echo set to true are messages sent by the bot
        # which we want to ignore.
        if(message.echo):
            return

        await self.handle_commands(message)

        if(self.trivia_started):
                   

    # here's where we handle the !trivia command
    @commands.command(name = 'trivia')
    async def trivia(self, ctx: commands.Context):
        endTrivia = False
        self.user = ctx.author.name

        # start the game loop, break on !endtrivia
        while(not self.endtrivia):
            await self.get_prompts()
            await self.prompt_user(ctx)
            await self.eval_response()

    @commands.command(name = 'endtrivia')
    async def endtrivia(self, ctx: commands.Context):

        if(self.endtrivia):
            return
        else:
            self.endtrivia = True

    async def get_prompts(self):
        rand = randint(0, 9)
        r = requests.get(url = TRIVIA_API_URL, params = TRIVIA_API_PARAMS)
        data = r.json()

        # store prompt data
        # print(data['results'][rand]['question'])
        self.prompt = data['results'][rand]['question']
        self.answer = data['results'][rand]['correct_answer']
        self.incorrect_answers = data['results'][rand]['incorrect_answers']

    async def prompt_user(self, ctx):
        await ctx.send(f'Here is your question, {self.user}: \n'
        f'{self.prompt} \n'
        f'Is it: \n'
        f'{self.incorrect_answers}'
        f'{self.answer}')

    async def eval_response(self):
        return

bot = Bot()
bot.run()
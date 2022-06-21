import requests
import json
import time
import datetime
from random import randint
from twitchio.ext import commands

TRIVIA_API_URL = 'https://opentdb.com/api.php?amount=10'
TRIVIA_API_PARAMS = {'prompt':'answer'}
TIMEOUT = 30

class TriviaBot(commands.Bot):
    adminName: str
    userName: str
    prompt: str
    answer: str
    candidates: dict
    trivia_started: bool
    starttime: float

    def __init__(self):
        f = open('config.json', "r")
        data = json.loads(f.read())
        print(data['secret'])
        print(data['channel'])
        print(data['adminName'])

        self.adminName = data['adminName']
        # init bot
        # super().__init__(token='zj3nhpbiun93gav6e4lth774qum4ql', prefix='!', initial_channels=['motorslam99'])
        super().__init__(token=data['secret'], prefix='!', initial_channels=[data['channel']])

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'User id is | {self.user_id}')

    # main loop
    async def event_message(self, message):
        # messages with echo set to true are from the bot (we want to ignore those)
        if(message.echo):
            return

        # blocking?
        await self.handle_commands(message)

        if(not self.trivia_started): return

        if(not self.userName == message.author.name): return

        if(round((time.time() - self.starttime)) >= TIMEOUT): 
            self.trivia_started = False
            await message.channel.send(f'Trivia ended, {self.userName}: you ran out of time!')

        if(message.content.lower() == 'a' or message.content.lower() == 'b' or
            message.content.lower() == 'c' or message.content.lower() == 'd'):

            if(message.content.lower() == self.answer):
                await message.channel.send(f'Correct')
            else:
                await message.channel.send(f'Incorrect. Correct answer was: {self.answer}. {self.candidates[self.answer]}')

            # ctx = await self.get_context(message=message)
            # await self.run_trivia(ctx)
        else:
            return

    # here's where we handle the !trivia command
    @commands.command(name = 'trivia')
    async def cmd_trivia(self, ctx: commands.Context):
        if(self.trivia_started): return

        self.trivia_started = True
        self.userName = ctx.author.name
        self.starttime = time.time()
        await self.run_trivia(ctx)

    @commands.command(name = 'endtrivia')
    async def cmd_endtrivia(self, ctx: commands.Context):
        # admin only command
        if(ctx.author.name == self.adminName):

            if(not self.trivia_started): return
            self.trivia_started = False
            await ctx.send('Trivia ended')

    # modify this function to work for other data sources
    async def get_prompts(self):
        # question_idx = randint(0, 9)
        
        # r = requests.get(url = TRIVIA_API_URL, params = TRIVIA_API_PARAMS)
        # data = r.json()

        f = open('config.json', "r")
        data = json.loads(f.read())

        answer_idx = randint(0, 3)
        question_idx = randint(0, data.keys())
        
        # store prompt data
        self.prompt = data['questions'][question_idx]['question']
        opts = {0: 'a', 1: 'b', 2: 'c', 3: 'd'}

        # store answer data mixed up
        self.candidates[opts[answer_idx]] = data['questions'][question_idx]['correct_answer']
        self.candidates[opts[(answer_idx + 1) % 4]] = data['questions'][question_idx]['incorrect_answers'][1]
        self.candidates[opts[(answer_idx + 2) % 4]] = data['questions'][question_idx]['incorrect_answers'][2]
        self.candidates[opts[(answer_idx + 3) % 4]] = data['questions'][question_idx]['incorrect_answers'][0]
        self.answer = opts[answer_idx]

    async def prompt_user(self, ctx: commands.Context):
        await ctx.send(f'Here is your question, {self.userName}: \n'
        f'{self.prompt} \n'
        'a. {a}\nb. {b}\nc. {c}\nd. {d}'.format(**self.candidates))

    async def run_trivia(self, ctx: commands.Context):
        await self.get_prompts()
        await self.prompt_user(ctx)


tBot = TriviaBot()
tBot.run()
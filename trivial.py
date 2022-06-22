import asyncio
import json
import time
import threading
import http.client
from random import randint
from twitchio.ext import commands

TRIVIA_API_URL = 'https://opentdb.com/api.php?amount=10'
TRIVIA_API_PARAMS = {'prompt':'answer'}
TIMEOUT = 1

class TriviaBot(commands.Bot):
    adminName = ''
    userName = ''
    prompt = ''
    answer = ''
    incorrect_answers = {}
    start_time = 0.0
    trivia_started = False

    def __init__(self):
        f = open('config.json', "r")
        data = json.loads(f.read())

        self.connect()

        self.trivia_started = False
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

        if(message.content.lower() == 'a' or message.content.lower() == 'b' or
            message.content.lower() == 'c' or message.content.lower() == 'd'):

            if(message.content.lower() == self.answer):
                await message.channel.send(f'Correct')
            else:
                await message.channel.send(f'Incorrect. Correct answer was: {self.answer}. {self.incorrect_answers[self.answer]}')

            self.trivia_started = False

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
        self.start_time = time.time()
        timer_thread = threading.Thread(target=self.timer_handler, args=(ctx,))
        timer_thread.start()
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
        f = open('config.json', "r")
        data = json.loads(f.read())

        answer_idx = randint(0, 3)
        question_idx = randint(0, len(data['questions']) - 1)
        print(question_idx)

        # store prompt data
        self.prompt = data['questions'][question_idx]['question']
        opts = {0: 'a', 1: 'b', 2: 'c', 3: 'd'}

        # store answer data mixed up
        self.incorrect_answers[opts[answer_idx]] = data['questions'][question_idx]['correct_answer']
        self.incorrect_answers[opts[(answer_idx + 1) % 4]] = data['questions'][question_idx]['incorrect_answers'][1]
        self.incorrect_answers[opts[(answer_idx + 2) % 4]] = data['questions'][question_idx]['incorrect_answers'][2]
        self.incorrect_answers[opts[(answer_idx + 3) % 4]] = data['questions'][question_idx]['incorrect_answers'][0]
        self.answer = opts[answer_idx]

    async def prompt_user(self, ctx: commands.Context):
        await ctx.send(f'Here is your question, {self.userName}: \n'
        f'{self.prompt} \n'
        'a. {a}\nb. {b}\nc. {c}\nd. {d}'.format(**self.incorrect_answers))

    async def run_trivia(self, ctx: commands.Context):
        await self.get_prompts()
        await self.prompt_user(ctx)

    async def timer(self, ctx: commands.Context):
        while(self.trivia_started):

            if(round((time.time() - self.start_time)) >= TIMEOUT):
                self.trivia_started = False
                await ctx.send(f'{self.userName} ran out of time!')

    def timer_handler(self, ctx: commands.Context):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(self.timer(ctx))
        loop.close()

    def connect(self):
        f = open('config.json', "r")
        data = json.loads(f.read())

        connection = http.client.HTTPSConnection('')
        payload = 'grant_type=client_credentials&client_id=' + data['clientID'] + '&client_secret=' + data['secret']
        headers = {'content-type': "application/x-www-form-urlencoded"}
        connection.request("POST", 'https://id.twitch.tv/oauth2/token', payload, headers)

        res = connection.getresponse()
        data = json.loads(res.read())
        print(data['access_token'])
        return data['access_token']


tBot = TriviaBot()
tBot.run()
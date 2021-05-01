from os import getenv
from random import choice, random

from discord import Activity, ActivityType, Embed, Intents
from discord.ext import commands
from dotenv import load_dotenv

import tasks

load_dotenv()
API_ACCESS = getenv('API_ACCESS')
authorized = [278589912184258562, 330188050275631105]

p = '!'
intents = Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=p, intents=intents)
bot.remove_command('help')

@bot.event
async def on_ready():
    print("phobot is ready to rumble")
    await bot.change_presence(
        activity=Activity(
            name="you download more ram",
            type=ActivityType.watching
        )
    )
    bot_channel = bot.get_channel(837755961963053146)
    await bot_channel.send("honk")


@bot.command(name='help', aliases=['h'])
async def help(ctx, *args):
    await ctx.send(
        "```"
        "Commands List:\n"
        f"{p}help       ({p}h)    Pulls up this page\n"
        f"{p}info       ({p}i)    Important links\n"
        f"{p}dashboard  ({p}d)    Personal task list\n"
        f"{p}complete   ({p}c)    Mark a task as complete\n"
        f"{p}report     ({p}rep)  Task overview (Logistics only)\n"
        f"{p}remindme   ({p}rem)  Adds a reminder\n"
        f"{p}positions  ({p}pos)  Yearbook position list"
        "```"
        "Contact FSgt Wang, Phoebe for bot help"
    )

@bot.command(name='info', aliases=['i'])
async def info(ctx, *args):
    await ctx.send(
        "Yearbook Google Drive link:\n"
        "<https://drive.google.com/drive/folders/1-6gNeptxnm-"
        "PN2NoHcBgvgRakhUH214t?usp=sharing>"
    )

@bot.command(name='dashboard', aliases=['d'])
async def dashboard(ctx, *args):
    user = ctx.message.set_author
    if args and args[0].startswith("<@") and args[0][2] == '!':
        user = ctx.guild.get_member(int(args[0][3:-1]))
    ROLES = {
        "Producers": 834978711055892530,
        "Writers": 836115355621392384,
        "Graphic Design": 836115375510781972,
        "Videography": 837158523221049386
    }
    colors = [(r.name, r.color.value) for r in user.roles if r.name in ROLES]
    await tasks.get_dashboard(ctx, user, colors)

@bot.command(name='complete', aliases=['c'])
async def complete(ctx, *args):
    await ctx.send("Task complete")

@bot.command(name='report', aliases=['rep'])
async def report(ctx, *args):
    await ctx.send("This is a report (tm)")

@bot.command(name='remindme', aliases=['rem'])
async def remind_me(ctx, *args):
    await ctx.send("Hi yes I am reminding you now")

@bot.command(name='addtask', aliases=['add'])
async def add_task(ctx, *args):
    if ctx.message.author.id in authorized:
        await tasks.add_task(ctx, args)

@bot.command(name='positions', aliases=['pos'])
async def positions(ctx, *args):
    await ctx.send(
        "```"
        "           YEARBOOK POSITIONS\n"
        "------------------------------------------\n"
        "Yearbook IC        | FSgt Wang, Phoebe\n"
        "Yearbook 2IC       | FSgt Zheng, Allen\n"
        "Producers          | FSgt Jaffery, Noorine\n"
        "                   | FSgt Ye, Dawson\n"
        "                   | FSgt Guo, William\n"
        "Graphic Design IC  | WO2 Yu, Adrian\n"
        "Graphic Design 2IC | WO2 Kwok, Felix\n"
        "Writers IC         | WO2 Zou, Alice\n"
        "Writers 2IC        | WO2 Kang, Angela"
        "```"
    )

# FUN COMMANDS

@bot.command(name='echo')
async def echo(ctx, *args):
    await ctx.message.delete()
    if not args:
        return
    if ctx.message.author.id in authorized:
        if args[0].startswith("<#"):
            channel = bot.get_channel(int(args[0][2:-1]))
            await channel.send(' '.join(args[1:]))
        else:
            await ctx.send(' '.join(args))

@bot.command(name='ram')
async def download_more_ram(ctx, *args):
    await ctx.send("DownloadMoreRAM.com")

@bot.command(name='corner')
async def corner(ctx, *args):
    chui = 279821782670639105
    if ctx.message.author.id == chui:
        await ctx.send("<@603002470398034000> GO TO YOUR CORNER")

@bot.event
async def on_message(message):
    phobot = 837832732276686888
    args = message.content.lower().split()
    honks = [len(k) - 3 if k.startswith('honk') else 0 for k in args]
    if message.author.id == phobot:
        return
    elif message.content.startswith(p):
        await bot.process_commands(message)
        return
    elif message.content.lower() in ['thanks phobot', 'thx phobot']:
        resp = choice(["ur welcome", "i accept paypal"])
        await message.channel.send(resp)
    elif any([m in args for m in ['hi', 'hello', 'hey']]):
        if random() < 0.1:
            await message.channel.send("Good morning to you too!")
    elif "goose" in args:
        await message.channel.send("HONK")
    elif honks and max(honks) > 0:
        await message.channel.send(f"HON{'K' * (max(honks) + 2)}")
    elif "short" in args or ("fsgt" in args and "ye" in args):
        await message.channel.send("Short? FSgt Ye? Synonymous.")
    elif "tall" in args or ("fsgt" in args and "wang" in args):
        await message.channel.send("Tall? FSgt Wang? Synonymous.")
    elif "bot" in args:
        if random() < 0.1:
            await message.channel.send("I'm always watching you.")
    elif "phobot" in args:
        await message.channel.send("You called?")
    elif "aot" in args:
        await message.channel.send("MIKASA?")
    elif "armin" in args:
        await message.channel.send(
            "https://media.tenor.com/images/e0c6bd4e1f2828629adc4b7e4a6d1b53"
            "/tenor.gif"
        )
    elif "late" in args:
        await message.channel.send("Early bird gets the worm!")
    elif "task" in args or "tasks" in args:
        await message.channel.send("I store tasks too! Use '!dashboard'")
    elif "dashboard" in args:
        await message.channel.send("Use '!dashboard'")

bot.run(API_ACCESS)

# TO DO
# Add task: return task ID

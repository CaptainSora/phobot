import asyncio
from os import getenv
from random import choice, random

from discord import Activity, ActivityType, Embed, Intents
from discord.ext import commands
from dotenv import load_dotenv

import reminders
import tasks
import SpellingBee.bee

load_dotenv()
API_ACCESS = getenv('API_ACCESS')
authorized = [278589912184258562, 330188050275631105]
ROLES = {
    # Name: (id, color)
    "Producers": (834978711055892530, 10181046),
    "Writers": (836115355621392384, 3447003),
    "Graphic Design": (836115375510781972, 15158332),
    "Videography": (837158523221049386, 3066993)
}

p = '!'
intents = Intents.default()
intents.members = True
bot = commands.Bot(command_prefix=p, intents=intents)
bot.remove_command('help')

# Helper functions
async def get_dm_channel(userid):
    user = bot.get_user(userid)
    if user is None:
        print(f"Failed to get user with id {userid}")
        return None
    dm_channel = user.dm_channel
    if dm_channel is None:
        dm_channel = await user.create_dm()
    backup_channel = bot.get_channel(837090104576835584)
    return dm_channel, backup_channel

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
    # Get users for report
    # userids = [
    #     279776665628835851, # FSgt Zheng, Allen
    #     273207697145462786, # WO2 Zou, Alice 
    #     809510270132944916, # WO2 Kang, Angela
    #     392471317086994436, # WO2 Yu, Adrian
    #     182601885046276097, # WO2 Kwok, Felix
    #     603002470398034000, # FSgt Ye, Dawson
    #     498320836772757505  # FSgt Guo, William
    # ]
    # users = [
    #     (bot_channel.guild.get_member(uid), await get_dm_channel(uid))
    #     for uid in userids 
    # ]
    # pho_channel = await get_dm_channel(330188050275631105)
    # while True:
    #     await reminders.send_reminders(get_dm_channel)
    #     await reminders.send_report(users, pho_channel[0])
    #     await asyncio.sleep(30 * 60)


@bot.command(name='help', aliases=['h'])
async def help(ctx, *args):
    await ctx.send(
        "```"
        "Commands List:\n"
        f"{p}help       ({p}h)    Pulls up this page\n"
        f"{p}info       ({p}i)    Yearbook Google Drive\n"
        f"{p}meetings   ({p}m)    Meeting Minutes + Recordings\n"
        f"{p}dashboard  ({p}d)    Personal task list\n"
        f"{p}complete   ({p}c)    Mark a task as complete\n"
        f"{p}report     ({p}rep)  Task overview (Logistics only)\n"
        f"{p}positions  ({p}pos)  Yearbook position list\n"
        f"{p}bee        ({p}b)    [Minigame] Daily Spelling Bee\n"
        f"{p}beelb      ({p}blb)  [Minigame] Spelling Bee Leaderboards"
        "```"
        "Contact FSgt Wang, Phoebe for bot help"
    )

@bot.command(name='info', aliases=['i'])
async def info(ctx, *args):
    await ctx.send(
        "Yearbook Google Drive:\n"
        "<https://drive.google.com/drive/folders/1-6gNeptxnm-"
        "PN2NoHcBgvgRakhUH214t?usp=sharing>\n\n"
        "Complete Task List Sheet:\n"
        "https://docs.google.com/spreadsheets/d/1hj2hfIIFE1LiByUKuAhZy"
        "J3ladu8uU2Os8R-S1GVFTE/edit?usp=sharing"
    )

@bot.command(name='meetings', aliases=['meeting', 'm'])
async def meetings(ctx, *args):
    await ctx.send(
        "Meeting Minutes + Recordings:\n"
        "https://drive.google.com/drive/folders/17pN71YY7QPbpBmRZoyLzXxeXDDGG"
        "Qr_b?usp=sharing"
    )

@bot.command(name='dashboard', aliases=['d'])
async def dashboard(ctx, *args):
    user = ctx.message.author
    if args and args[0].startswith("<@") and args[0][2] == '!':
        user = ctx.guild.get_member(int(args[0][3:-1]))
    colors = [(r.name, r.color.value) for r in user.roles if r.name in ROLES]
    await tasks.get_dashboard(ctx, user, colors)

@bot.command(name='complete', aliases=['c'])
async def complete(ctx, *args):
    await tasks.complete_task(ctx, args)

@bot.command(name='report', aliases=['rep'])
async def report(ctx, *args):
    user = ctx.message.author
    try:
        if "Logistics" not in [r.name for r in user.roles]:
            await ctx.send(
                "This command is restricted to the Logistics role."
            )
            return
    except AttributeError:
        await ctx.send(
            "Unhandled AttributeError - If you have the logistics role, please"
            " try again."
        )
        return
    colors = []
    if args:
        team = ' '.join(args).title()
        if team in ROLES:
            colors.append((team, ROLES[team][1]))
        else:
            colors.append((team, None))
    else:
        colors = [
            (r.name, r.color.value) for r in user.roles if r.name in ROLES
        ]
    await tasks.get_report(ctx, user, colors)

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

# Auth required

@bot.command(name='addtask')
async def add_task(ctx, *args):
    if ctx.message.author.id in authorized:
        await tasks.add_task(ctx, args)

@bot.command(name='add')
async def false_add_task(ctx, *args):
    await ctx.send("Did you mean: '!addtask'?")

@bot.command(name='deltask')
async def rem_task(ctx, *args):
    if ctx.message.author.id in authorized:
        await tasks.remove_task(ctx, args)

@bot.command(name='changedue')
async def change_due(ctx, *args):
    if ctx.message.author.id in authorized:
        await tasks.change_task_due(ctx, args)

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
    await ctx.send("https://DownloadMoreRAM.com")

@bot.command(name='join', aliases=['play', 'p'])
async def poor_rythm(ctx, *args):
    await ctx.send("<@235088799074484224> has been demoted to the ? prefix")

@bot.command(name='corner')
async def corner(ctx, *args):
    chui = 279821782670639105
    if ctx.message.author.id == chui:
        await ctx.send("<@603002470398034000> GO TO YOUR CORNER")

@bot.command(name='bee', aliases=['b'])
async def spelling_bee_wrapper(ctx, *args):
    await SpellingBee.bee.spelling_bee(ctx, args)

@bot.command(name='beelb', aliases=['blb'])
async def spelling_bee_lb_wrapper(ctx, *args):
    await SpellingBee.bee.bee_leaderboards(ctx, args)

@bot.event
async def on_message(message):
    phobot = 837832732276686888
    args = message.content.lower().split()
    honks = [
        len(k) - 3
        if k.startswith('honk') and k[-1] == 'k' else 0
        for k in args
    ]
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
        if random() < 0.1:
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
    elif "dashboard" in args:
        await message.channel.send("Use '!dashboard'")
    elif message.content == "E":
        await message.channel.send(
            "https://tenor.com/view/ea-sports-e-ea-meme-gif-14922519"
        )

bot.run(API_ACCESS)

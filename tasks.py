from datetime import datetime

from discord import Embed

import database

RED = 0xd60606
GREEN = 0x00bd5b
ROLES = {
    "Producers": 834978711055892530,
    "Writers": 836115355621392384,
    "Graphic Design": 836115375510781972,
    "Videography": 837158523221049386
}

async def add_task(ctx, args):
    embed=Embed(
        title='Add Task',
        color=RED
    )
    # Verify arguments
    arglist = [
        s.strip() for s in ' '.join(args).replace(' | ', '|').split('|')
    ]
    if len(arglist) != 4 or not all(arglist):
        embed.description = (
            "Function usage:\n"
            "!addtask [task name] | [team] | [assigned to] | [due date]\n"
            "task name: the name of the task\n"
            f"team: one of ({', '.join(ROLES.keys())})\n"
            "assigned to: a list of member pings\n"
            "due date: date + time in the format 'Jan 1, 23:30'"
        )
        await ctx.send(embed=embed)
        return
    # Parameter 2
    if arglist[1].title() not in ROLES:
        embed.description = (
            f"Parameter 2: 'team' must be one of ({', '.join(ROLES.keys())}) "
            "as text."
        )
        await ctx.send(embed=embed)
        return
    # Parameter 3
    assigned_to_list = [s.strip().replace('!', '') for s in arglist[2].split()]
    if not all([s[0] == "<" and s[-1] == ">" for s in assigned_to_list]):
        embed.description = (
            "Parameter 3: 'assigned to' must be a list of member pings."
        )
        await ctx.send(embed=embed)
        return
    # Parameter 4
    try:
        due_date = datetime.strptime(arglist[3], "%b %d, %H:%M")
    except ValueError:
        embed.description = (
            "Parameter 4: 'due date' must be a date and time in the format "
            "'Jan 1, 23:30'."
        )
        await ctx.send(embed=embed)
        return
    # Complete
    embed.color = GREEN
    task_id = database.insert_task(
        arglist[0], arglist[1], assigned_to_list, arglist[3]
    )
    embed.description = (
        f"Successfully added task ID:{task_id} to database."
    )
    await ctx.send(embed=embed)

async def get_dashboard(ctx, user, colors):
    tasks = sorted(
        database.get_tasks(),
        key=lambda t: datetime.strptime(t['due_date'], "%b %d, %H:%M")
    )
    embed=Embed(
        title='Task Dashboard',
        color=0x95a5a6 # default
    )
    embed.set_author(
        name=user.nick,
        icon_url=user.avatar_url
    )
    if colors:
        embed.description = colors[0][0]
        embed.color = colors[0][1]
    for t in tasks:
        assigned_to_list = t['assigned_to'].split(',')
        if f"<@{user.id}>" not in assigned_to_list:
            continue
        # Emoji formatting
        cur_time = datetime.now()
        due_time = datetime.strptime(t['due_date'], "%b %d, %H:%M")
        due_time = due_time.replace(year=cur_time.year)
        check = ' :white_check_mark:' if t['complete_date'] is not None else ''
        alert = ' :warning:' if not check and cur_time > due_time else ''
        # Embed
        embed.add_field(
            name=f"{t['task_name']} - ID:{t['task_id']}",
            value=(
                f"Due NLT {t['due_date']}{check}{alert}"
            ),
            inline=False
        )
    await ctx.send(embed=embed)

async def get_report(ctx, user, colors, ping=False):
    tasks = sorted(
        database.get_tasks(),
        key=lambda t: datetime.strptime(t['due_date'], "%b %d, %H:%M")
    )
    embed=Embed(
        title='Task Report',
        color=0x95a5a6 # default
    )
    embed.set_author(
        name=user.nick,
        icon_url=user.avatar_url
    )
    if colors:
        if colors[0][1] is None:
            embed.description = (
                f"'{colors[0][0]}' is not a valid team name.\n"
                f"Please choose one of {({', '.join(ROLES.keys())})}."
            )
            await ctx.send(embed=embed)
            return
        embed.description = colors[0][0]
        embed.color = colors[0][1]
    numfields = 0
    page = 1
    if ping:
        await ctx.send(
            f"<@{user.id}>, <@330188050275631105> - Automated report"
        )
    for t in tasks:
        assigned_to_list = t['assigned_to'].split(',')
        if colors[0][0] != t['task_team']:
            continue
        # Emoji formatting
        cur_time = datetime.now()
        due_time = datetime.strptime(t['due_date'], "%b %d, %H:%M")
        due_time = due_time.replace(year=cur_time.year)
        check = ' :white_check_mark:' if t['complete_date'] is not None else ''
        alert = ' :warning:' if not check and cur_time > due_time else ''
        # Embed
        embed.add_field(
            name=f"{t['task_name']} - ID:{t['task_id']}",
            value=(
                f"Assigned to {', '.join(assigned_to_list)}\n"
                f"Due NLT {t['due_date']}{check}{alert}"
            ),
            inline=False
        )
        numfields += 1
        if numfields >= 24:
            embed.set_footer(text=f"Page {page}")
            await ctx.send(embed=embed)
            embed.clear_fields()
            page += 1
            numfields = 0
    if numfields > 0:
        if page > 1:
            embed.set_footer(text=f"Page {page}")
        await ctx.send(embed=embed)

async def complete_task(ctx, args):
    user_id = ctx.author.id
    embed=Embed(
        title='Complete Task',
        color=RED
    )
    if len(args) < 1 or not args[0].isdecimal():
        embed.description = (
            "Function usage:\n"
            "!complete [id]\n"
            "id: the task id"
        )
        await ctx.send(embed=embed)
        return
    task_id = int(args[0])
    tasks = database.get_tasks(ext=f"WHERE task_id = {task_id}")
    if not tasks:
        embed.description = (
            f"Task with ID:{task_id} not found."
        )
        await ctx.send(embed=embed)
        return
    assigned_to = [int(i[2:-1]) for i in tasks[0]['assigned_to'].split(',')]
    if user_id not in assigned_to:
        embed.description = (
            f"Task with ID:{task_id} not assigned to <@{user_id}>."
        )
        await ctx.send(embed=embed)
        return
    database.complete_task(task_id)
    embed.color = GREEN
    embed.description = (
        f"Task with ID:{task_id} marked as complete."
    )
    await ctx.send(embed=embed)

async def remove_task(ctx, args):
    embed=Embed(
        title='Remove Task',
        color=RED
    )
    if len(args) < 1 or not args[0].isdecimal():
        embed.description = (
            "Function usage:\n"
            "!remtask [id]\n"
            "id: the task id"
        )
        await ctx.send(embed=embed)
        return
    task_id = int(args[0])
    tasks = database.get_tasks(ext=f"WHERE task_id = {task_id}")
    if not tasks:
        embed.description = (
            f"Task id {task_id} not found."
        )
        await ctx.send(embed=embed)
        return
    database.remove_task(task_id)
    embed.color = GREEN
    embed.description = (
        f"Successfully removed task id {task_id}."
    )
    await ctx.send(embed=embed)

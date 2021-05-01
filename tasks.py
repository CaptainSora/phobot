from datetime import datetime

from discord import Embed

import database

async def add_task(ctx, args):
    ROLES = {
        "Producers": 834978711055892530,
        "Writers": 836115355621392384,
        "Graphic Design": 836115375510781972,
        "Videography": 837158523221049386
    }
    embed=Embed(
        title='Add Task',
        color=0xd60606 # red
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
    assigned_to_list = [s.strip() for s in arglist[2].split()]
    if not all([s[0] == "<" and s[-1] == ">" for s in assigned_to_list]):
        embed.description = (
            "Parameter 3: 'assigned to' must be a list of member pings."
        )
        await ctx.send(embed=embed)
        return
    # Parameter 4
    try:
        print(arglist[3])
        due_date = datetime.strptime(arglist[3], "%b %d, %H:%M")
    except ValueError:
        embed.description = (
            "Parameter 4: 'due date' must be a date and time in the format "
            "'Jan 1, 23:30'."
        )
        await ctx.send(embed=embed)
        return
    # Complete
    embed.color = 0x00bd5b # green
    database.insert_task(arglist[0], arglist[1], assigned_to_list, arglist[3])
    embed.description = (
        "Successfully added task to database."
    )
    await ctx.send(embed=embed)

async def get_dashboard(ctx, user, colors):
    tasks = database.get_tasks()
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
        if f"<@!{user.id}>" not in assigned_to_list:
            continue
        embed.add_field(
            name=f"{t['task_name']} - ID:{t['task_id']}",
            value=(
                f"Due NLT {t['due_date']}"
                f"{':white_check_mark:' * (t['complete_date'] is not None)}"
            ),
            inline=False
        )
    await ctx.send(embed=embed)
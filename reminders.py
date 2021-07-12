from datetime import datetime

from discord import Forbidden

import database
import tasks
from vars import ROLES

# ROLES = {
#     # Name: (id, color)
#     "Producers": (834978711055892530, 10181046),
#     "Writers": (836115355621392384, 3447003),
#     "Graphic Design": (836115375510781972, 15158332),
#     "Videography": (837158523221049386, 3066993)
# }

LAST_REPORT = None

async def send_reminders(get_dm_channel):
    rem_ids = []
    cur_time = datetime.now()
    reminders = database.get_reminders()
    for r in reminders:
        rem_time = datetime.strptime(r['rem_date'], "%b %d, %H:%M")
        rem_time = rem_time.replace(year=cur_time.year)
        if cur_time < rem_time:
            continue
        # Prepare message
        rem_str = ""
        if r['rem_type'] == 0:
            rem_str = "OVERDUE"
        elif r['rem_type'] == 1:
            rem_str = "Due in 1 day"
        rem_str += f": '{r['task_name']}', ID:{r['task_id']}"
        # Send reminder
        assigned_ids = [
            int(userid[2:-1]) for userid in r['assigned_to'].split(',')
        ]
        for uid in assigned_ids:
            dm_channel, backup_channel = await get_dm_channel(uid)
            try:
                await dm_channel.send(rem_str)
            except Forbidden:
                print(f"User {uid} has blocked DMs")
                rem_str = f"<@{uid}> {rem_str}"
                await backup_channel.send(rem_str)
        # Add to list of ids to remove
        rem_ids.append(r['rem_id'])
    # Remove reminders if sent
    database.remove_reminders(rem_ids)

async def send_report(users, pho_channel):
    global LAST_REPORT
    cur_time = datetime.now()
    cur_date = cur_time.strftime("%b %d")
    # Check for 9AM, and if sent already today
    if cur_time.hour != 9 or LAST_REPORT == cur_date:
        return
    for user, dm_ch in users:
        # dm_ch is (dm_ch, backup_ch)
        colors = [
            (r.name, r.color.value) for r in user.roles if r.name in ROLES
        ]
        await tasks.get_report(dm_ch[0], user, colors)
        await tasks.get_report(pho_channel, user, colors)
    LAST_REPORT = cur_date

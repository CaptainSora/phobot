import asyncio
from datetime import datetime

from discord import Forbidden

import database


async def send_reminders(get_dm_channel):
    while True:
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
                int(userid[3:-1]) for userid in r['assigned_to'].split(',')
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
        # Remove reminders if send
        database.remove_reminders(rem_ids)
        # Wait 30 mins
        await asyncio.sleep(30 * 60)

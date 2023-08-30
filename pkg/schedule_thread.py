import datetime

from croniter import croniter
import threading
from pkg.qqbot.process import process_message
from mirai import Plain, MessageChain
from pkg.plugin.host import PluginHost
from plugins.QChatSchedule.pkg.sql import *


def task(id, croniter: croniter, plugin_host: PluginHost):
    schedule = get_schedule_by_id(id)
    if schedule[8] == "on_going":
        logging.info(f"执行定时任务：{schedule[0]}")
        reply = process_message(schedule[2], schedule[3], schedule[4], MessageChain.parse_obj([schedule[4]]), schedule[5])
        next_time = croniter.get_next(datetime.datetime)
        delay = (next_time - datetime.datetime.now()).total_seconds()
        threading.Timer(delay, task, args=(id, croniter, plugin_host)).start()


def run_schedule(plugin_host: PluginHost):
    schedule_list = get_all_schedules()
    logging.info(f"开始运行所有定时任务")
    time_list = [[i[0], croniter(i[1], datetime.datetime.now())] for i in schedule_list if i[8] == 'on_going']
    for i in time_list:
        logging.info(f"开始运行{i[0]}")
        next_time = i[1].get_next(datetime.datetime)
        delay = (next_time - datetime.datetime.now()).total_seconds()
        threading.Timer(delay, task, args=(i[0], i[1], plugin_host)).start()

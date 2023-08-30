import json
import os
import threading
import time
from datetime import datetime

import pytz
from croniter import croniter

from plugins.QChatSchedule.pkg.schedule_thread import task
from pkg.plugin.models import *
from pkg.plugin.host import EventContext, PluginHost
from plugins.QChatSchedule.pkg.schedule_thread import run_schedule
from plugins.QChatSchedule.pkg.sql import *


def run(schedule: tuple, plugin_host):
    croniter_i = croniter(schedule[1], datetime.now())
    next_time = croniter_i.get_next(datetime)
    delay = (next_time - datetime.now()).total_seconds()
    threading.Timer(delay, task, args=(schedule[0], croniter_i, plugin_host)).start()


# 注册插件
@register(
    name="QChatSchedule",
    description="设置定时任务",
    version="0.1",
    author="oliverkirk-sudo",
)
class QChatSchedulePlugin(Plugin):
    def __init__(self, plugin_host: PluginHost):
        self.plugin_host = plugin_host
        create_schedule()
        with open(os.path.join(os.getcwd(), "plugins/switch.json"), "r", encoding='utf-8') as f:
            switch = json.load(f)
        if switch['QChatSchedule']['enabled'] == "true":
            run_schedule(plugin_host)

    @on(PersonCommandSent)
    @on(GroupCommandSent)
    def schedule_command(self, event: EventContext, **kwargs):
        if kwargs["command"] in ["定时", "schedule"] and kwargs["is_admin"]:
            launcher_type = kwargs["launcher_type"]
            launcher_id = kwargs["launcher_id"]
            sender_id = kwargs["sender_id"]
            if len(kwargs["params"]) == 0:
                event.add_return("reply", ["请输入参数"])
            elif kwargs["params"][0] in ["every", "每"]:
                if kwargs["params"][2] in ["hour", "时", "小时"]:
                    if kwargs["params"][4] in ["minute", "分钟", "分"]:
                        cron = f"{kwargs['params'][3]} */{kwargs['params'][1]} * * *"
                        command = ''
                        for i in range(5, len(kwargs["params"])):
                            command += kwargs["params"][i]
                            command += " "
                        schedule = add_in_schedule(
                            cron,
                            launcher_type,
                            launcher_id,
                            command,
                            sender_id,
                        )
                        run(schedule, self.plugin_host)
                if kwargs["params"][2] in ["minute", "分钟", "分"]:
                    cron = f"*/{kwargs['params'][1]} * * * *"
                    command = ''
                    for i in range(3, len(kwargs["params"])):
                        command += kwargs["params"][i]
                        command += " "
                    schedule = add_in_schedule(
                        cron,
                        launcher_type,
                        launcher_id,
                        command,
                        sender_id,
                    )
                    run(schedule, self.plugin_host)
                    event.add_return("reply", ["添加成功"])
                else:
                    event.add_return("reply", ["添加失败"])
            elif kwargs["params"][0] == "add":
                if kwargs["params"][1].count("?") == 4:
                    cron_list = kwargs["params"][1].splite("?")
                    cron = f"{cron_list[0]} {cron_list[1]} {cron_list[2]} {cron_list[3]} {cron_list[4]}"
                    command = ''
                    for i in range(2, len(kwargs["params"])):
                        command += kwargs["params"][i]
                        command += " "
                    if cron != "":
                        schedule = add_in_schedule(
                            cron,
                            launcher_type,
                            launcher_id,
                            command,
                            sender_id,
                        )
                        run(schedule, self.plugin_host)
                        event.add_return("reply", ["添加成功"])
                    else:
                        event.add_return("reply", ["添加失败"])
            elif kwargs["params"][0] in ["off", "关闭"]:
                if kwargs["params"][1] in ["all", "所有"]:
                    off_all()
                    event.add_return("reply", ["关闭所有任务成功"])
                else:
                    off_one(kwargs["params"][1])
                    event.add_return("reply", [f"关闭{kwargs['params'][1]}任务成功"])
                pass
            elif kwargs["params"][0] in ["on", "开启"]:
                if kwargs["params"][1] in ["all", "所有"]:
                    on_all()
                    event.add_return("reply", ["开启所有任务成功"])
                else:
                    on_one(kwargs["params"][1])
                    event.add_return("reply", [f"开启{kwargs['params'][1]}任务成功"])
            elif kwargs["params"][0] in ["delete", "删除"]:
                if kwargs["params"][1] in ["all", "所有"]:
                    delete_all()
                    event.add_return("reply", ["删除所有任务成功"])
                else:
                    delete_one(kwargs["params"][1])
                    event.add_return("reply", [f"删除{kwargs['params'][1]}任务成功"])
            elif kwargs["params"][0] == "help":
                help_str = """
                
                """
                pass
            elif kwargs["params"][0] == "show":
                if kwargs["params"][1] == "all":
                    schedule = get_all_schedules()
                    print(schedule)
                    show_str = ''
                    if len(schedule) > 0:
                        for i in schedule:
                            show_str += f'''任务ID：{i[0]}\n定时器：{i[1]}\n发送类型：{i[2]}\n发送id：{i[3]}\n指令：{i[4]}\n创建者id：{i[5]}\n创建时间：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i[6]))}\n状态：{i[8]}\n#####################'''
                        event.add_return("reply", [show_str])
                    else:
                        event.add_return("reply", ["列表为空"])
                else:
                    schedule = get_schedule_by_id(kwargs["params"][1])
                    show_str = f'''任务ID：{schedule[0]}\n定时器：{schedule[1]}\n发送类型：{schedule[2]}\n发送id：{schedule[3]}\n指令：{schedule[4]}\n创建者id：{schedule[5]}\n创建时间：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(schedule[6]))}\n状态：{schedule[8]}\n#####################'''
                    event.add_return("reply", [show_str])
            else:
                event.add_return("reply", ["指令格式出错"])
            event.prevent_default()
            event.prevent_postorder()

    # 插件卸载时触发
    def __del__(self):
        pass

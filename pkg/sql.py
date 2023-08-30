import time

from pkg.database.manager import DatabaseManager
import logging


def create_schedule():
    databasemanager = DatabaseManager()
    """创建数据表"""
    databasemanager.__execute__(
        """create table if not exists `schedule` (
        `id` INTEGER PRIMARY KEY,
        `cron` varchar(255) not null,
        `type` varchar(255) not null,
        `number` bigint not null,
        `command` longtext not null,
        `create_by` bigint not null,
        `create_timestamp` bigint not null,
        `last_interact_timestamp` bigint not null,
        `status` varchar(255) not null default 'on_going'
    )"""
    )
    logging.info("创建schedule数据库成功")


def add_in_schedule(cron, type, number, command, create_by):
    databasemanager = DatabaseManager()
    id = len(get_all_schedules())
    sql = """
    insert into `schedule`(
    id,cron,type,number,command,create_by,create_timestamp,last_interact_timestamp,status
    ) values(
    '{}','{}','{}','{}','{}','{}','{}','{}','{}'
    )
    """.format(
        id, cron, type, number, command, create_by, int(time.time()), 0, "on_going"
    )
    databasemanager.__execute__(sql)
    logging.info("添加定时任务成功")
    return get_all_schedules()[-1]


def get_all_schedules():
    databasemanager = DatabaseManager()
    sql = "SELECT * FROM `schedule`"
    databasemanager.__execute__(sql)
    results = databasemanager.cursor.fetchall()
    return results


def get_schedule_by_id(id):
    databasemanager = DatabaseManager()
    sql = """
    SELECT * FROM `schedule` WHERE id = {}
    """.format(
        id
    )
    databasemanager.__execute__(sql)
    results = databasemanager.cursor.fetchone()
    return results


def update_schedule_status(id, status):
    databasemanager = DatabaseManager()
    sql = "UPDATE `schedule` SET status = '{}' WHERE id = {}".format(status, id)
    databasemanager.__execute__(sql)


def off_all():
    databasemanager = DatabaseManager()
    sql = "UPDATE `schedule` SET status = '{}'".format("off")
    databasemanager.__execute__(sql)


def on_all():
    databasemanager = DatabaseManager()
    sql = "UPDATE `schedule` SET status = '{}'".format("on_going")
    databasemanager.__execute__(sql)


def delete_all():
    databasemanager = DatabaseManager()
    sql = "DELETE FROM `students`"
    databasemanager.__execute__(sql)


def off_one(id):
    databasemanager = DatabaseManager()
    sql = "UPDATE `schedule` SET status = '{}' WHERE id = {}".format("off", id)
    databasemanager.__execute__(sql)


def on_one(id):
    databasemanager = DatabaseManager()
    sql = "UPDATE `schedule` SET status = '{}' WHERE id = {}".format("on_going", id)
    databasemanager.__execute__(sql)
    return get_all_schedules()[id]


def delete_one(id):
    databasemanager = DatabaseManager()
    sql = "DELETE FROM `students` WHERE id = {}".format(id)
    databasemanager.__execute__(sql)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from datetime import datetime
from typing import Text


def count_milliseconds(access_start=datetime.now(), access_end=datetime.now()):
    """
    计算时间
    :return:
    """
    return (access_end - access_start).seconds * 1000


def timestamp_conversion(time_str: Text) -> int:
    """
    时间戳转换，将日期格式转换成时间戳
    :param time_str: 时间  '2023-05-06 17:04:00'
    :return: 1683363840000
    """

    try:
        datetime_format = datetime.strptime(str(time_str), "%Y-%m-%d %H:%M:%S")
        return int(
            time.mktime(datetime_format.timetuple()) * 1000.0
            + datetime_format.microsecond / 1000.0
        )
    except ValueError as exc:
        raise ValueError('日期格式错误, 需要传入得格式为 "%Y-%m-%d %H:%M:%S" ') from exc


def time_conversion(time_num: int):
    """
    时间戳转换成日期
    :param time_num: 1683363840000
    :return: 2023-05-06 17:04:00
    """
    if isinstance(time_num, int):
        time_stamp = float(time_num / 1000)
        time_array = time.localtime(time_stamp)
        return time.strftime("%Y-%m-%d %H:%M:%S", time_array)


def now_time():
    """
    获取当前时间, 日期格式: 2023-05-08 17:06:04
    :return:
    """
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return localtime


def now_time_day():
    """
    获取当前时间, 日期格式: 2023-05-08
    :return:
    """
    localtime = time.strftime("%Y-%m-%d", time.localtime())
    return localtime


def get_time_for_min(minute: int) -> int:
    """
    获取几分钟后的时间戳
    @param minute: 分钟 3
    @return: N分钟后的时间戳  1683536984000
    """
    return int(time.time() + 60 * minute) * 1000


def get_now_time() -> int:
    """
    获取当前时间戳, 整形
    @return: 当前时间戳 1683536804000
    """
    return int(time.time()) * 1000


if __name__ == '__main__':
    print(timestamp_conversion('2023-05-06 17:04:00'))
    print(time_conversion(1683363840000))
    print(now_time())
    print(now_time_day())
    print(get_time_for_min(3))
    print(get_now_time())

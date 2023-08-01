#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import json
import os
import re
import time
from typing import List

import pytest
import requests

from common.config import TOKEN_FILE, PRE_DATA_DIR
from utils.log.log_control import LogHandler
from utils.cache.cache_control import CacheHandler
from utils.other.json_control import JsonHandler
from utils.other.yaml_control import GetYamlCaseData


# 每天自动获取token更新到token.json中,并加到缓存
@pytest.fixture(scope='session', autouse=True)
def set_token():
    #获取token.json的内容
    token_dic = JsonHandler(TOKEN_FILE).get_json_data()
    #当前时间
    current_time = datetime.datetime.now().strftime('%Y-%m-%d')
    #获取token时间
    token_time = token_dic['time']

    if current_time > token_time:
        token_yaml = f'{PRE_DATA_DIR}Token.yaml'
        pre_data = GetYamlCaseData(token_yaml).get_yaml_case_data()['Token']
        response = requests.request(method=pre_data['method'], url=pre_data['url'], headers=pre_data['header'],
                                    params=pre_data['params'], verify=False)
        res = json.loads(response.text)
        token_dic['time'] = current_time
        token = f"Bearer {res['data']['token']['token']}"
        token_dic['token'] = token
        JsonHandler(TOKEN_FILE).set_json_data(token_dic)
        CacheHandler.update_cache(cache_name='token', value=token)
    else:
        CacheHandler.update_cache(cache_name='token', value=token_dic['token'])



def pytest_collection_modifyitems(items: List["Item"]) -> None:
    for item in items:
        item.name = item.name.encode('utf-8').decode('unicode-escape')
        # 目录包含中文会乱码，使用正则匹配处理单独处理unicode
        regular_pattern = r"\[(.*?)]"
        if key_list := re.findall(regular_pattern, item._nodeid):  # 正则匹配到的值集合['host()', 'host()']
            for key in key_list:
                value = key.encode('utf-8').decode('unicode-escape')
                pattern = re.compile(regular_pattern)
                item._nodeid = re.sub(pattern, f"[{str(value)}]", item._nodeid)  # 把host替换成config文件的值
        #item._nodeid = item.nodeid.encode('utf-8').decode('unicode-escape')

    # 期望用例顺序
    # test_updatelawyerrelease 为用例名称，py文件里的函数
    # 例 ：appoint_items = ["test_updatelawyerrelease"]
    appoint_items = []

    # 指定运行顺序
    # items = [<Function test_deletelawyerrelease[删除曝光接口]>, <Function test_getlawyerreleaselistbyh5[小程序查询接口]>]
    run_items = []     # [<Function test_updatelawyerrelease[更新小法律师曝光]>]
    for i in appoint_items:
        for item in items:
            module_item = item.name.split("[")[0]
            if i == module_item:
                run_items.append(item)

    for i in run_items:
        run_index = run_items.index(i)   #0 在run_items里的索引
        items_index = items.index(i)    #5  在item里的索引
        #期待运行索引与实际运行索引不同，则替换执行位置
        if run_index != items_index:
            items[items_index], items[run_index] = items[run_index], items[items_index]


# def pytest_configure(config):
#     config.addinivalue_line("markers", 'smoke')
#     config.addinivalue_line("markers", '回归测试')

# 如果使用多线程会有统计问题
def pytest_terminal_summary(terminalreporter):
    """
    收集测试结果
    """
    m = LogHandler(os.path.basename(__file__))
    _TOTAL = terminalreporter._numcollected
    _TIMES = time.time() - terminalreporter._sessionstarttime
    _PASSED = len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown'])
    _ERROR = len([i for i in terminalreporter.stats.get('error', []) if i.when != 'teardown'])
    _FAILED = len([i for i in terminalreporter.stats.get('failed', []) if i.when != 'teardown'])
    _SKIPPED = len([i for i in terminalreporter.stats.get('skipped', []) if i.when != 'teardown'])
    m.info(f"用例总数: {_TOTAL}")
    m.info(f"成功用例数：{_PASSED}")
    m.info(f"异常用例数: {_ERROR}")
    m.info(f"失败用例数: {_FAILED}")
    m.info(f"跳过用例数: {_SKIPPED}")
    m.info("用例执行时长: %.2f" % _TIMES + " s")
    try:
        _RATE = _PASSED / _TOTAL * 100
        m.info("用例成功率: %.2f" % _RATE + " %")
    except ZeroDivisionError:
        m.info("错误，用例成功率: 0.00 %")
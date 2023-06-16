#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import json
import pytest
import requests

from common.config import TOKEN_FILE, PRE_DATA_DIR
from common.utils.ReadJson import JsonHandle
from common.utils.ReadYaml import GetYamlCaseData


# @pytest.fixture(scope="session", autouse=False)
# def clear_report():
#     """如clean命名无法删除报告，这里手动删除"""
#     del_file(ensure_path_sep("\\report"))


#每天自动获取token更新到token.json中
@pytest.fixture(scope='session',autouse=True)
def set_token():
    #获取token.json的内容
    token_dic = JsonHandle(TOKEN_FILE).get_json_data()
    #当前时间
    current_time = datetime.datetime.now().strftime('%Y-%m-%d')
    #获取token时间
    token_time = token_dic['time']

    if current_time > token_time:
        token_yaml = f'{PRE_DATA_DIR}Token.yaml'
        pre_data = GetYamlCaseData(token_yaml).get_yaml_case_data()['Token']
        response = requests.request(method=pre_data['method'], url=pre_data['url'],headers=pre_data['header'],params=pre_data['params'],verify=False)
        res = json.loads(response.text)
        token_dic['time'] = current_time
        token_dic['token'] = f"Bearer {res['data']['token']['token']}"
        JsonHandle(TOKEN_FILE).set_json_data(token_dic)


# def pytest_collection_modifyitems(items):
#     """
#     测试用例收集完成时，将收集到的 item 的 name 和 node_id 的中文显示在控制台上
#     :return:
#     """
#     for item in items:
#         item.name = item.name.encode("utf-8").decode("unicode_escape")
#         item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")
#
#     # 期望用例顺序
#     # print("收集到的测试用例:%s" % items)
#     appoint_items = ["test_get_user_info", "test_collect_addtool", "test_Cart_List", "test_ADD", "test_Guest_ADD",
#                      "test_Clear_Cart_Item"]
#
#     # 指定运行顺序
#     run_items = []
#     for i in appoint_items:
#         for item in items:
#             module_item = item.name.split("[")[0]
#             if i == module_item:
#                 run_items.append(item)
#
#     for i in run_items:
#         run_index = run_items.index(i)
#         items_index = items.index(i)
#
#         if run_index != items_index:
#             n_data = items[run_index]
#             run_index = items.index(n_data)
#             items[items_index], items[run_index] = items[run_index], items[items_index]


# def pytest_configure(config):
#     config.addinivalue_line("markers", 'smoke')
#     config.addinivalue_line("markers", '回归测试')


# @pytest.fixture(scope="function", autouse=True)
# def case_skip(in_data):
#     """处理跳过用例"""
#     in_data = TestCase(**in_data)
#     if ast.literal_eval(cache_regular(str(in_data.is_run))) is False:
#         allure.dynamic.title(in_data.detail)
#         allure_step_no(f"请求URL: {in_data.is_run}")
#         allure_step_no(f"请求方式: {in_data.method}")
#         allure_step("请求头: ", in_data.headers)
#         allure_step("请求数据: ", in_data.data)
#         allure_step("依赖数据: ", in_data.dependence_case_data)
#         allure_step("预期数据: ", in_data.assert_data)
#         pytest.skip()

# @pytest.fixture(scope='session')
# def pytest_terminal_summary(terminalreporter):
#     """
#     收集测试结果
#     """
#     m = LogHandler(os.path.basename(__file__))
#     _PASSED = len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown'])
#     _ERROR = len([i for i in terminalreporter.stats.get('error', []) if i.when != 'teardown'])
#     _FAILED = len([i for i in terminalreporter.stats.get('failed', []) if i.when != 'teardown'])
#     _SKIPPED = len([i for i in terminalreporter.stats.get('skipped', []) if i.when != 'teardown'])
#     _TOTAL = terminalreporter._numcollected
#     _TIMES = time.time() - terminalreporter._sessionstarttime
#     m.info(f"用例总数: {_TOTAL}")
#     m.info(f"成功用例数：{_PASSED}")
#     m.info(f"异常用例数: {_ERROR}")
#     m.info(f"失败用例数: {_FAILED}")
#     m.info(f"跳过用例数: {_SKIPPED}")
#     m.info("用例执行时长: %.2f" % _TIMES + " s")
#
#     try:
#         _RATE = _PASSED / _TOTAL * 100
#         m.info("用例成功率: %.2f" % _RATE + " %")
#     except ZeroDivisionError:
#         m.info("用例成功率: 0.00 %")

import pytest

from common.allure.allure_tools import allure_step


def case_skip(in_data):
    """处理跳过用例"""
    allure_step("请求头: ", in_data.headers)
    allure_step("请求数据: ", in_data.requestData)
    pytest.skip()

import ast
import os
import sys
from typing import Dict, Text

import requests
import urllib3

from common.assertion.assert_control import AssertExecution
from common.db.mysql_control import SqlHandler
from common.decorator.allure_decorator import allure_decorator
from common.decorator.assert_decorator import assert_decorator
from common.decorator.database_decorator import database_sql_assert
from common.decorator.request_decorator import request_decorator
from common.decorator.runtime_decorator import execution_duration
from common.decorator.teardown_decorator import teardown_decorator
from common.log.log_control import LogHandler
from common.unit import case_skip
from common.unit.dependent_case import DependentCase
from common.unit.setup_control import setup_handler
from common.utils.models import TestCase, RequestType, ResponseData
from common.utils.regular_control import yaml_case_regular

sys.path.append(os.path.dirname(sys.path[0]))


class RequestSend:
    def __init__(self, yaml_case):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.log = LogHandler(os.path.basename(__file__))
        self.__yaml_case = TestCase(**yaml_case)
        self.mysql = SqlHandler()

    @staticmethod
    def response_elapsed_total_seconds(res) -> float:
        """获取接口响应时长"""
        try:
            return round(res.elapsed.total_seconds() * 1000, 2)
        except AttributeError:
            return 0.00

    def request_type_for_json(
            self,
            headers: Dict,
            method: Text,
            **kwargs):
        """ 判断请求类型为json格式 传dict"""
        return requests.request(
            method=method,
            url=self.__yaml_case.url,
            json=self.__yaml_case.requestData,
            headers=headers,
            verify=False,
            **kwargs
        )

    def request_type_for_params(
            self,
            headers: Dict,
            method: Text,
            **kwargs):
        """处理 requestType 为 params 传dict"""
        return requests.request(
            method=method,
            url=self.__yaml_case.url,
            params=self.__yaml_case.requestData,
            headers=headers,
            verify=False,
            **kwargs
        )

    def request_type_for_data(
            self,
            headers: Dict,
            method: Text,
            **kwargs):
        """判断 requestType 为 data 类型"""
        return requests.request(
            method=method,
            url=self.__yaml_case.url,
            data=self.__yaml_case.requestData,
            headers=headers,
            verify=False,
            **kwargs
        )

    def _database_assert_handler(self):
        """处理 sql 参数 ：数据库校验"""
        from common.utils import config
        # 数据库校验开关
        if config.mysql.switch:
            # 判断database_assert_sql的类型是否为list类型（excel读取是str类型，判断第一个字符是否为'['）
            if self.__yaml_case.database_assert_sql and self.__yaml_case.database_assert_sql[0] == '[':
                _database_assert_sql = ast.literal_eval(self.__yaml_case.database_assert_sql)
                _database_assert_result = ast.literal_eval(self.__yaml_case.database_assert_result)
            else:
                _database_assert_sql = self.__yaml_case.database_assert_sql
                _database_assert_result = self.__yaml_case.database_assert_result

            # 判断不为空才执行校验   assert_sql：可能为sql或None ；sql_assert：可能为0或1或None。 None不执行
            if _database_assert_sql and _database_assert_result is not None:
                return AssertExecution().assert_execution(_database_assert_sql, _database_assert_result)
        else:
            self.log.info("数据库校验已关闭，用例不进行数据库校验")

    def _check_params(
            self,
            res,
            yaml_data: "TestCase",
            is_decorator: bool = True
    ) -> "ResponseData":
        """
        :param res:
        :param yaml_data:
        :return: 处理接口返回及测试用例，返回一个通用的数据
        """
        _data = {
            "yaml_is_run": yaml_data.is_run,
            "yaml_remark": yaml_data.remark,
            "yaml_body": yaml_data.requestData,
            "yaml_assert_data": yaml_data.assert_data,
            "yaml_data": yaml_data,
            "yaml_database_assert_sql": self.__yaml_case.database_assert_sql,
            "yaml_database_assert_result": self.__yaml_case.database_assert_result,

            "req_url": res.url,
            "req_method": res.request.method,
            "req_headers": res.request.headers,

            "res_assert_result": None,
            "res_data": res.text,
            "res_cookie": res.cookies,
            "res_time": self.response_elapsed_total_seconds(res),
            "res_status_code": res.status_code,

            "file": os.path.basename(__file__),
            "is_decorator": is_decorator

        }

        # 抽离出通用模块，判断 http_request 方法中的一些数据校验
        return ResponseData(**_data)

    @teardown_decorator  # 后置条件装饰器
    @assert_decorator  # 断言装饰器
    @allure_decorator  # allure步骤装饰器
    @request_decorator(switch=True)  # 接口请求装饰器（打印请求信息日志）
    @database_sql_assert  # 数据库校验装饰器  返回res_sql_result
    @execution_duration(3000)  # 封装统计函数执行时间装饰器
    def http_request(self, is_decorator=True, **kwargs):
        """
        :param dependent_switch: True
        :param is_decorator: 用于判断是否执行装饰器，True执行，False不执行，主要用于关联接口时不需要执行装饰器
        :param kwargs:
        :return:
        """
        # 判断yaml文件的is_run参数是否执行用例
        if self.__yaml_case.is_run is True or self.__yaml_case.is_run is None:
            # 非依赖要执行的接口时 执行前置条件
            # if not dependence:
            setup_handler(self.__yaml_case)
            # 如果有依赖数据统一在那边做处理，否则直接处理缓存
            if self.__yaml_case.dependence_case is True:
                # 把self.__yaml_case传到DependentCase类处理，返回正则匹配到的数据
                self.__yaml_case = DependentCase(self.__yaml_case).get_dependent_data()
            else:
                # self.__yaml_case做缓存替换处理
                self.__yaml_case = yaml_case_regular(self.__yaml_case)

            requests_type_mapping = {
                RequestType.JSON.value: self.request_type_for_json,
                RequestType.DATA.value: self.request_type_for_data,
                RequestType.PARAMS.value: self.request_type_for_params
                # RequestType.FILE.value: self.request_type_for_file,
                # RequestType.NONE.value: self.request_type_for_none,
                # RequestType.EXPORT.value: self.request_type_for_export
            }
            # requests_type_mapping.get(self._yaml_case.requestType) 执行的函数，比如JSON，执行request_type_for_json的函数
            res = requests_type_mapping.get(self.__yaml_case.requestType)(
                headers=self.__yaml_case.headers,
                method=self.__yaml_case.method,
                **kwargs
            )
            # 判断用例关联依赖，不执行装饰器
            return (
                self._check_params(
                    res=res, yaml_data=self.__yaml_case
                )
                if is_decorator
                else self._check_params(res=res, yaml_data=self.__yaml_case, is_decorator=False)
            )
        else:
            self.log.info(f'[{self.__yaml_case.remark}]用例不执行')
            case_skip()


if __name__ == '__main__':
    # from common.config import TESTDATA_DIR
    from common.file_tools.get_yaml_data_analysis import CaseData
    from common.config import TESTDATA_DIR

    file = f'{TESTDATA_DIR}xiaofa/案源竞价/order_create.yaml'

    case_data = CaseData(file).case_process(case_id_switch=False)
    _yaml_data = case_data[0]
    # print(yaml_data)
    RequestSend(_yaml_data).http_request()

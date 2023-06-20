import requests
import urllib3
import sys
import os
import ast
from typing import Dict, Text, Union
from common.allure.allure_tools import allure_step
from common.db.MysqlHelper import SqlHandle
from common.unit.TeardownDecorator import teardown_decorator
from common.utils.ReadJson import JsonHandle
from common.log.LogDecorator import request_decorator
from common.log.run_time_decorator import execution_duration
from common.log.LogHandler import LogHandler
from common.utils.models import TestCase, RequestType, ResponseData
from common.config import TOKEN_FILE
from common.assertion.assert_control import AssertExecution

sys.path.append(os.path.dirname(sys.path[0]))


class RequestSend:
    def __init__(self, yaml_case):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.log = LogHandler(os.path.basename(__file__))
        self.__yaml_case = TestCase(**yaml_case)
        self.mysql = SqlHandle()

    def response_elapsed_total_seconds(self, res) -> float:
        """获取接口响应时长"""
        try:
            return round(res.elapsed.total_seconds() * 1000, 2)
        except AttributeError:
            return 0.00

    def check_headers_data(
            self,
            headers: Dict) -> Dict:
        """
        headers参数校验
        @return:
        """
        # headers = ast.literal_eval(cache_regular(str(headers)))
        # 判断authorization参数是否在headers中，存在且为True 执行
        if any(i == 'authorization' for i in headers.keys()) and headers['authorization']:
            headers['authorization'] = JsonHandle(TOKEN_FILE).get_json_data()['token']
        return headers

    def request_type_for_json(
            self,
            headers: Dict,
            method: Text,
            is_setup: bool = False,
            **kwargs):
        """ 判断请求类型为json格式 传dict"""
        # kwargs其他传入的参数，判断是否更新请求参数的值（用于前置请求后查询数据库的值作为请求参数）
        if kwargs:
            self.__yaml_case.requestData[kwargs['is_yield']['key']] = kwargs['is_yield']['value']
        _headers = self.check_headers_data(headers)
        # 用例的前置接口请求
        if is_setup:
            _requestData = self.__yaml_case.process['setup']['request']['requestData']
            _url = self.__yaml_case.process['setup']['request']['host'] + self.__yaml_case.process['setup']['request'][
                'url']
        # 用例的接口请求
        else:
            _requestData = self.__yaml_case.requestData
            _url = self.__yaml_case.url
        return requests.request(
            method=method,
            url=_url,
            json=_requestData,
            headers=_headers,
            verify=False,
        )

    def request_type_for_params(
            self,
            headers: Dict,
            method: Text,
            is_setup: bool = False,
            **kwargs):
        """处理 requestType 为 params 传dict"""
        # kwargs其他传入的参数，判断是否更新请求参数的值（用于前置请求后查询数据库的值作为请求参数）
        if kwargs:
            self.__yaml_case.requestData[kwargs['is_yield']['key']] = kwargs['is_yield']['value']
        _headers = self.check_headers_data(headers)
        # 用例的前置接口请求
        if is_setup:
            _requestData = self.__yaml_case.process['setup']['request']['requestData']
            _url = self.__yaml_case.process['setup']['request']['host'] + self.__yaml_case.process['setup']['request'][
                'url']
        # 用例的接口请求
        else:
            _requestData = self.__yaml_case.requestData
            _url = self.__yaml_case.url
        return requests.request(
            method=method,
            url=_url,
            headers=_headers,
            verify=False,
            params=_requestData,
        )

    def request_type_for_data(
            self,
            headers: Dict,
            method: Text,
            is_setup: bool = False,
            **kwargs):
        """判断 requestType 为 data 类型"""
        # kwargs其他传入的参数，判断是否更新请求参数的值（用于前置请求后查询数据库的值作为请求参数）即 is_yield参数
        if kwargs:
            self.__yaml_case.requestData[kwargs['is_yield']['key']] = kwargs['is_yield']['value']
        _headers = self.check_headers_data(headers)
        # 用例的前置接口请求
        if is_setup:
            _requestData = self.__yaml_case.process['setup']['request']['params']
            _url = self.__yaml_case.process['setup']['request']['host'] + self.__yaml_case.process['setup']['request'][
                'url']
        # 用例的接口请求
        else:
            _requestData = self.__yaml_case.requestData
            _url = self.__yaml_case.url
        return requests.request(
            method=method,
            url=_url,
            data=_requestData,
            headers=_headers,
            verify=False,
        )

    def _sql_data_handler(self):
        """处理 sql 参数 ：数据库校验"""
        from common.utils import config
        # 数据库校验开关
        if config.mysql['mysql_db_switch']:
            # 判断sql_data的类型是否为list类型（excel读取是str类型，判断第一个字符是否为'['）
            if self.__yaml_case.sql_data and self.__yaml_case.sql_data[0] == '[':
                sql_data = ast.literal_eval(self.__yaml_case.sql_data)
                sql_assert = ast.literal_eval(self.__yaml_case.sql_assert)
            else:
                sql_data = self.__yaml_case.sql_data
                sql_assert = self.__yaml_case.sql_assert
            # 判断不为空才执行校验   sql_data：可能为sql或None ；sql_assert：可能为0或1或None。 None不执行
            if sql_data and sql_assert is not None:
                return AssertExecution().assert_execution(sql_data, sql_assert)
        else:
            self.log.info(f"数据库校验已关闭，用例不进行数据库校验")

    def _check_params(
            self,
            res,
            yaml_data: "TestCase",
            sql_result: Union[bool, None]
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

            "sql_result": sql_result,
            "req_url": res.url,
            "req_method": res.request.method,
            "req_headers": res.request.headers,

            "res_data": res.text,
            "res_cookie": res.cookies,
            "res_time": self.response_elapsed_total_seconds(res),
            "res_status_code": res.status_code,
            "file": os.path.basename(__file__)

        }

        # 抽离出通用模块，判断 http_request 方法中的一些数据校验
        return ResponseData(**_data)

    def request_type(self, headers=None):
        """通过headers判断请求类型(前置请求时使用)"""
        if headers is None or 'Content-Type' not in headers.keys():
            # return None
            return 'params'
        if 'application/json' in headers['Content-Type']:
            return 'json'
        elif 'application/form-data' in headers['Content-Type']:
            return 'params'
        elif 'application/x-www-form-urlencoded' in headers['Content-Type']:
            return 'data'
        else:
            return None

    def setup_handle(self, requests_type_mapping):
        """前置条件的数据处理"""
        # 如果process参数所有key不包含‘setup’，返回 None（全部为Ture才执行）
        if all('setup' not in i for i in self.__yaml_case.process.keys()):
            return None
        setup_data = self.__yaml_case.process['setup']
        setup_key_list = list(setup_data.keys())
        is_yield = {}
        for data in setup_key_list:
            # 前置-sql数据处理
            if 'sql' in data.lower():
                if 'num' in data.lower():
                    self.mysql.data_type(setup_data[data], state='num')
                else:
                    self.mysql.data_type(setup_data[data])
            # 前置-接口数据处理
            if 'request' in data.lower():
                method = setup_data[data]['method']
                headers = setup_data[data]['headers']
                request_type = self.request_type(headers)

                headers['authorization'] = JsonHandle(TOKEN_FILE).get_json_data()['token']
                requests_type_mapping.get(request_type.upper())(headers, method, is_setup=True)
            # 前置-查询数据库返回到请求参数处理
            if 'is_yield' in data.lower():
                is_yield_data = setup_data[data]
                is_yield_data_list = list(is_yield_data.keys())
                # 遍历is_yield_data_list
                for k in is_yield_data_list:
                    # k包含'num'字段，则查询数量 （case_num）  查询num return 1
                    if 'num' in k:
                        result = self.mysql.select(is_yield_data[k], state='num')
                        is_yield['key'] = k.split('_')[0]
                        is_yield['value'] = result

                    else:
                        # 判断数据库是否有值来返回到用例里  查询one return (1,)
                        if result := self.mysql.select(is_yield_data[k], state='one'):
                            is_yield['key'] = k
                            is_yield['value'] = result[0]
        return is_yield

    @classmethod
    def api_allure_step(
            cls,
            *,
            url: Text,
            headers: Text,
            method: Text,
            data: Text,
            assert_data: Text,
            res_time: Text,
            res: Text,
            sql_result: bool
    ) -> None:
        """ 在allure中记录请求数据 """
        allure_step("请求URL: ", url)
        allure_step("请求方式: ", method)
        allure_step("请求头: ", headers)
        allure_step("请求数据: ", data)
        allure_step("数据库校验结果: ", sql_result)
        allure_step("校验数据: ", assert_data)
        allure_step("响应耗时(ms): ", res_time)
        allure_step("响应结果: ", res)

    @teardown_decorator
    @execution_duration(3000)
    @request_decorator(switch=True)
    def http_request(self, **kwargs):
        # 判断yaml文件的is_run参数是否执行用例
        if self.__yaml_case.is_run or self.__yaml_case.is_run is None:
            requests_type_mapping = {
                RequestType.JSON.value: self.request_type_for_json,
                RequestType.DATA.value: self.request_type_for_data,
                RequestType.PARAMS.value: self.request_type_for_params
                # RequestType.FILE.value: self.request_type_for_file,
                # RequestType.NONE.value: self.request_type_for_none,
                # RequestType.EXPORT.value: self.request_type_for_export
            }
            # requests_type_mapping.get(self._yaml_case.requestType) 执行的函数，比如JSON，执行request_type_for_json的函数
            # 判断执行前置条件后是否有返回值
            if _is_yield := self.setup_handle(requests_type_mapping):
                res = requests_type_mapping.get(self.__yaml_case.requestType)(
                    headers=self.__yaml_case.headers,
                    method=self.__yaml_case.method,
                    is_yield=_is_yield,
                    **kwargs
                )
            else:
                res = requests_type_mapping.get(self.__yaml_case.requestType)(
                    headers=self.__yaml_case.headers,
                    method=self.__yaml_case.method,
                    **kwargs
                )

            # 数据库校验
            _sql_result = self._sql_data_handler()

            # 转换格式
            _res_data = self._check_params(
                res=res,
                yaml_data=self.__yaml_case,
                sql_result=_sql_result
            )
            # 添加allure步骤
            self.api_allure_step(
                url=_res_data.req_url,
                headers=str(_res_data.req_headers),
                method=_res_data.req_method,
                data=str(_res_data.yaml_body),
                assert_data=str(_res_data.yaml_assert_data),
                res_time=str(_res_data.res_time),
                res=_res_data.res_data,
                sql_result=_sql_result
            )
            return _res_data

        else:
            self.log.info(f'{self.__yaml_case.remark}用例不执行')


if __name__ == '__main__':
    # from common.config import TESTDATA_DIR
    from common.file_tools.get_yaml_data_analysis import CaseData
    from common.config import TESTDATA_DIR

    file = f'{TESTDATA_DIR}xiaofa/案源竞价/order_create.yaml'

    case_data = CaseData(file).case_process(case_id_switch=False)
    yaml_data = case_data[0]
    # print(yaml_data)
    RequestSend(yaml_data).http_request()

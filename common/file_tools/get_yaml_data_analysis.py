#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import os
from typing import Union, Text, List

from common.utils.cache_control import CacheHandler
from common.utils.models import RequestType, Method, TestCaseEnum, TestCase
from common.utils.yaml_control import GetYamlCaseData


class CaseDataCheck:
    """
    yaml 数据解析, 判断数据填写是否符合规范
    """

    def __init__(self, file_path):
        self.file_path = file_path
        if os.path.exists(self.file_path) is False:
            raise FileNotFoundError("用例地址未找到")
        self.case_data = None
        self.case_id = None

    def _assert(self, attr: Text):
        """
        检查参数是否在测试用例中
        :param attr:  models文件的TestCaseEnum的参数
        :return:
        """
        assert attr in self.case_data.keys(), (
            f"用例ID为 {self.case_id} 的用例中缺少 {attr} 参数，请确认用例内容是否编写规范."
            f"当前用例文件路径：{self.file_path}"
        )

    def check_params_exit(self):
        """
        读取models文件的TestCaseEnum，如果值为True则检查 参数是否在测试用例中
        :return:
        """
        for enum in list(TestCaseEnum._value2member_map_.keys()):
            if enum[1]:
                self._assert(enum[0])

    def check_params_right(self, enum_name, attr):
        """
        判断attr是否在model对应的enum_name函数里
        例子：检查case_data的requestType
        :param enum_name: <enum 'RequestType'>
        :param attr: data
        enum_name._member_names_ 输出RequestType类的所有name的列表['JSON', 'PARAMS', 'DATA', 'FILE', 'EXPORT', 'NONE']
        :return: 大写attr
        """

        _member_names_ = enum_name._member_names_
        assert attr.upper() in _member_names_, (
            f"用例ID为 {self.case_id} 的用例中 {attr} 填写不正确，"
            f"当前框架中只支持 {_member_names_} 类型."
            f"如需新增 method 类型，请联系管理员."
            f"当前用例文件路径：{self.file_path}"
        )
        return attr.upper()

    @property
    def get_method(self) -> Text:
        # TestCaseEnum.METHOD.value[0]  method
        # self.case_data.get(TestCaseEnum.METHOD.value[0])) post
        return self.check_params_right(
            Method,
            self.case_data.get(TestCaseEnum.METHOD.value[0])
        )

    @property
    def get_host(self) -> Text:
        return self.case_data.get(TestCaseEnum.HOST.value[0]) + self.case_data.get(TestCaseEnum.URL.value[0])

    @property
    def get_headers(self):
        headers = self.case_data.get(TestCaseEnum.HEADERS.value[0])
        if 'authorization' in headers.keys() and headers['authorization'] is True:
            headers['authorization'] = CacheHandler.get_cache('token')
        return headers

    @property
    def get_request_type(self):
        """
        传models的RequestType类 ，requestType
        :return:
        """
        return self.check_params_right(
            RequestType,
            self.case_data.get(TestCaseEnum.REQUEST_TYPE.value[0])
        )

    @property
    def get_database_assert_sql(self) -> Union[list, Text, None]:
        return self.case_data.get(TestCaseEnum.DATABASE_ASSERT_SQL.value[0])

    @property
    def get_database_assert_result(self) -> Union[list, Text, None]:
        return self.case_data.get(TestCaseEnum.DATABASE_ASSERT_RESULT.value[0])

    @property
    def get_dependence_case_data(self):
        if _dep_data := self.case_data.get(TestCaseEnum.DE_CASE.value[0]):
            assert self.case_data.get(TestCaseEnum.DE_CASE_DATA.value[0]) is not None, (
                f"程序中检测到您的 case_id 为 {self.case_id} 的用例存在依赖，但是 {_dep_data} 缺少依赖数据."
                f"如已填写，请检查缩进是否正确， 用例路径: {self.file_path}"
            )
        return self.case_data.get(TestCaseEnum.DE_CASE_DATA.value[0])

    @property
    def get_assert(self):
        _assert_data = self.case_data.get(TestCaseEnum.ASSERT_DATA.value[0])
        assert _assert_data is not None, (
            f"用例ID 为 {self.case_id} 未添加断言，用例路径: {self.file_path}"
        )
        return _assert_data


class CaseData(CaseDataCheck):
    """获取yaml文件的用例数据"""

    def case_process(self, case_id_switch: Union[None, bool] = None):
        data = GetYamlCaseData(self.file_path).get_yaml_case_data()
        case_list = []
        for key, values in data.items():
            # 公共配置中的数据，与用例数据不同，需要单独处理
            if key != 'case_common':
                self.case_data = values
                self.case_id = key
                # 检查model参数是否在测试用例中
                super().check_params_exit()
                _case_data = {
                    'method': self.get_method,
                    'is_run': self.case_data.get(TestCaseEnum.IS_RUN.value[0]),
                    'url': self.get_host,
                    'remark': self.case_data.get(TestCaseEnum.REMARK.value[0]),
                    'headers': super().get_headers,
                    'requestType': super().get_request_type,
                    'requestData': self.case_data.get(TestCaseEnum.REQUEST_DATA.value[0]),
                    'dependence_case': self.case_data.get(TestCaseEnum.DE_CASE.value[0]),
                    'dependence_case_data': self.get_dependence_case_data,
                    'setup_sql': self.case_data.get(TestCaseEnum.SETUP_SQL.value[0]),
                    # "current_request_set_cache": self.case_data.get(TestCaseEnum.CURRENT_RE_SET_CACHE.value[0]),
                    "database_assert_sql": self.get_database_assert_sql,
                    "database_assert_result": self.get_database_assert_result,
                    "assert_data": self.get_assert,
                    # "sleep": self.case_data.get(TestCaseEnum.SLEEP.value[0]),
                    "teardown": self.case_data.get(TestCaseEnum.TEARDOWN.value[0])
                }
                if case_id_switch is True:
                    case_list.append({key: TestCase(**_case_data).dict()})
                else:
                    case_list.append(TestCase(**_case_data).dict())
        return case_list


class GetTestCase:
    """用例执行时获取Cache数据，初始化执行的test_case目录的__init__.py"""

    @staticmethod
    def get_case_data(case_id_lists: List):
        # 用例数据集合
        case_lists = []
        for i in case_id_lists:
            _data = CacheHandler.get_cache(i)
            case_lists.append(_data)
        return case_lists


if __name__ == '__main__':
    from common.config import TESTDATA_DIR

    file = f'{TESTDATA_DIR}xiaofa/抽盲盒活动/lottery_time.yaml'
    case_data = CaseData(file).case_process(case_id_switch=True)
    print(json.dumps(case_data[0], ensure_ascii=False))

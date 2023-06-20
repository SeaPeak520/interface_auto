import ast
import json
import os
from typing import Any, Text, Union

import allure
from common.utils.models import load_module_functions, AssertMethod
from common.assertion import assert_type
from common.utils.FileHelper import get_value
from common.exceptions.exceptions import AssertTypeError, DataAcquisitionFailed, ValueTypeError
from common.log.LogHandler import LogHandler
from common.db.MysqlHelper import SqlHandle

class AssertUtil:
    def __init__(self, assert_data, response_data, status_code, request_data=None):
        """
        :param assert_data:  yaml文件中assert的数据
        :param response_data: 请求接口返回的数据
        :param request_data: yaml文件中requestData的数据
        """
        self.assert_data = assert_data
        self.response_data = response_data
        self.request_data = request_data
        self.status_code = status_code
        self.log = LogHandler(os.path.basename(__file__))

    # 获取assert_data的dict数据
    @property
    def get_assert_data_all(self):
        """
        :return: {'stata_code': 200 , 'code': {'jsonpath': '$.code', 'type': '==', 'value': 200, 'AssertType': None, 'meassage': '状态码不一致'}}
        """
        #校验self.assert_data数据不为空
        assert self.assert_data is not None, f"{self.__class__.__name__} 应该包含一个 assert data 属性"

        return ast.literal_eval(str(self.assert_data))

    def get_type(self, get_assert_data):
        """
        # 判断type、value、jsonpath、AssertType是否在key里，并返回value
        # 获取断言类型对应的枚举值
        #self.get_assert_data.get("type") 为'=='
        #AssertMethod(self.get_assert_data.get("type")).name 为 'equals'

        :return: equals
        """
        assert 'type' in get_assert_data.keys(), f" 断言数据: {get_assert_data} 中缺少 `type` 属性 "
        name = AssertMethod(get_assert_data.get("type")).name
        return name

    def get_value(self, get_assert_data):
        """
        获取assert_data的 key为value的值
        :return: 200
        """
        assert 'value' in get_assert_data.keys(), f" 断言数据: {get_assert_data} 中缺少 `value` 属性 "
        return get_assert_data.get("value")

    def get_jsonpath(self, get_assert_data):
        """
        获取assert_data的 key为jsonpath的值
        :return: $.code
        """
        assert 'jsonpath' in get_assert_data.keys(), f" 断言数据: {get_assert_data} 中缺少 `jsonpath` 属性 "
        return get_assert_data.get("jsonpath")

    def get_assert_type(self, get_assert_data):
        """
        获取assert_data的 key为AssertType的值
        :return: None
        """
        assert 'AssertType' in get_assert_data.keys(), f" 断言数据: {get_assert_data} 中缺少 `AssertType` 属性 "
        return get_assert_data.get("AssertType")

    @staticmethod
    def functions_mapping():
        """
        # 通过变量get_type 动态获取assert_type文件的方法，并传值执行
        获取assert_type的各个方法的内存地址
        :return:{'equals': <function equals at 0x000002916CE884A0>, 'less_than': <function less_than at 0x000002916CF2E200>....}
        """
        return load_module_functions(assert_type)

    def _assert(self, get_type, check_value: Any, expect_value: Any, message: Text = ""):
        """
        :param check_value:  要校验的值
        :param expect_value:  预期值
        :param message:  预期不符提示的信息
        :return: self.functions_mapping()[self.get_type]执行assert_type文件的equals方法
        """
        self.functions_mapping()[get_type](check_value, expect_value, str(message))

    @property
    def get_response_data(self):
        return json.loads(self.response_data)

    def get_message(self, get_assert_data):
        """
        获取断言描述，如果未填写，则返回 `None`
        :return:
        """
        return get_assert_data.get("message", None)

    @property
    def get_status_code(self):
        """
        获取断言描述，如果未填写，则返回 `None`
        :return:
        """
        return self.get_assert_data_all.get("status_code", None)

    def _assert_resp_data(self, get_assert_data):
        """
        通过$.code使用jsonpath获取到response的数据
        :return:
        """
        resp_data = get_value(self.get_response_data, self.get_jsonpath(get_assert_data))
        assert resp_data is not False, (
            f"jsonpath数据提取失败，提取对象: {self.get_response_data} , 当前语法: {self.get_jsonpath(get_assert_data)}"
        )
        return resp_data if len(resp_data) > 1 else resp_data[0]

    def _assert_request_data(self, get_assert_data):
        """
        通过$.code使用jsonpath获取到request_data的数据
        :return:
        """
        req_data = get_value(self.request_data, self.get_jsonpath(get_assert_data))
        assert req_data is not False, (
            f"jsonpath数据提取失败,提取对象: {self.request_data} , 当前语法: {self.get_jsonpath(get_assert_data)}"
        )
        return req_data if len(req_data) > 1 else req_data[0]

    @allure.step('进行断言检验')
    def assert_type_handle(self):
        """
        get_type 获取判断类型 equals
        _assert_resp_data   通过jsonpath在response_data匹配到的值
        get_value  yaml文件获取assert_data的 key为value的值
        get_message  yaml文件获取assert_data的 key为message的值
        :return:
        """
        for i in self.get_assert_data_all.keys():
            if i == 'status_code':
                try:
                    self._assert('equals', self.status_code, self.get_status_code, '状态码不一致')
                except AssertionError as e:
                    self.log.error(f'状态码不一致[{self.status_code},{self.get_status_code}]')
                    raise e

            else:
                #{'jsonpath': '$.code', 'type': '==', 'value': 200, 'AssertType': None, 'meassage': '状态码不一致'}
                _assert_data = self.get_assert_data_all.get(i)
                if self.get_assert_type(_assert_data) == "R_SQL":
                    self._assert(self._assert_request_data(_assert_data), self.get_sql_data,
                                 self.get_message(_assert_data))

                # 判断请求参数为响应数据库断言
                elif self.get_assert_type(_assert_data) in ["SQL", "D_SQL"]:
                    self._assert(self._assert_resp_data(_assert_data), self.get_sql_data, self.get_message)

                # 判断非数据库断言类型
                elif self.get_assert_type(_assert_data) is None:
                    try:
                        self._assert(self.get_type(_assert_data), self._assert_resp_data(_assert_data),
                                 self.get_value(_assert_data), self.get_message(_assert_data))
                    except AssertionError as e:
                        self.log.error(f'校验错误，信息：[{self._assert_resp_data(_assert_data)},{self.get_value(_assert_data)}]{self.get_message(_assert_data)}')
                        raise e
                    except AssertTypeError as e:
                        self.log.error(f"校验类型不正确: {self.get_assert_type(_assert_data)}")
                        raise e

                else:
                    raise AssertTypeError("断言失败，目前只支持数据库断言和响应断言")


class AssertExecution(SqlHandle):
    """ 处理断言sql数据 """
    def assert_execution(self, sql_data: Union[list,Text], sql_assert: Union[list,Text]):
        """
         执行 sql, 负责处理 yaml 文件中的断言需要执行多条 sql 的场景，最终会把所有数据校验后，以布尔类型返回
        :param sql_data: sql
        :param sql_assert: 校验数据（数量）
        :return:
        """
        try:
            if isinstance(sql_data,str):
                # 判断sql_data和sql_assert是否符合书写规范
                if not sql_data and not sql_assert:
                    return None
                if (sql_data and not sql_assert) or (not sql_data and sql_assert):
                    raise BaseException("校验语句和校验值不匹配，请检查")

                if sql_data:
                    #判断sql的语法
                    _sql_type = ['update', 'delete', 'insert', 'select']
                    if all(i not in sql_data for i in _sql_type):
                        raise DataAcquisitionFailed("数据库校验的sql语句语法有问题")
                    # 执行sql获取数量，然后做校验
                    num = self.data_type(sql_data,state='num')
                    assert_type.equals(num,int(sql_assert),'数据库校验不通过')
                    return True
            elif isinstance(sql_data, list):
                #判断sql_data和sql_assert是否符合书写规范
                if not sql_data and not sql_assert:
                    return None
                if len(sql_data) != len(sql_assert):
                    raise BaseException("校验语句和校验值不匹配，请检查")

                #对sql_data进行遍历
                for k,sql in enumerate(sql_data):
                    #判断sql和校验值是否为空
                    if (sql and not sql_assert[k]) or (not sql and sql_assert[k]):
                        raise BaseException("校验语句和校验值不匹配，请检查")

                    if sql:
                        #判断sql的语法
                        _sql_type = ['update', 'delete', 'insert', 'select']
                        if all(i not in sql for i in _sql_type):
                            raise DataAcquisitionFailed("数据库校验的sql语句语法有问题")
                        #执行sql获取数量，然后做校验
                        num = self.data_type(sql,state='num')
                        assert_type.equals(num,int(sql_assert[k]),'数据库校验不通过')
                        return True
            else:
                raise ValueTypeError("sql数据类型不正确，接受的是list或str")
        except Exception as error_data:
            self.log.error(f"数据库连接失败，失败原因: {error_data}")
            raise error_data

if __name__ == '__main__':
    from common.utils.ReadYaml import YamlHandler
    from common.utils.DirHelper import ensure_path_sep

    yaml_data = YamlHandler(ensure_path_sep('E:\\pythonProject\\new/data/test.yaml')).get_yaml_data()

    assert_data = yaml_data['caseCollectAdd']['assert']
    response_data = '{"cod":200,"messag":"操作成功","data":"收藏成功"}'
    # request_data = yaml_data['caseCollectAdd']['requestData']
    status_code = 20

    au = AssertUtil(assert_data, response_data, status_code)
    au.assert_type_handle()

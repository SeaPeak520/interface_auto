import ast
import json
import os

from common.config import TESTDATA_FILE, TESTDATA_DIR
from common.log.log_control import LogHandler
from common.utils.dir_control import mk_dir, ensure_path_sep
from common.utils.excel_control import ExcelHandler
from common.utils.file_control import create_file
from common.utils.yaml_control import YamlHandler


class FromExcelWriteYaml():
    def __init__(self):
        # 创建日志对象
        self.log = LogHandler(os.path.basename(__file__))
        # 创建excel对象
        self.excel_handle = ExcelHandler(TESTDATA_FILE)

    # 获取测试文件的sheet名称列表 ['xiaofa', 'Sheet4']
    @property
    def get_sheet(self):
        return self.excel_handle.get_sheet

    def dataHandle_json(self, data):
        """数据判空处理并转换JSON格式"""
        return json.dumps(data) if data else None

    def dataHandle_dict(self, data):
        """数据判空处理并转换DICT格式"""
        return json.loads(data) if data else {}

    def dataConvert(self, data):
        """数据判空处理并使用ast.literal_eval转换格式"""
        return ast.literal_eval(data) if data else None

    def dataHandle_int(self, data):
        """数据判空处理并转换INT格式"""
        return int(data) if data else None

    def judge_is_null(self, data, is_null=False, message=''):
        """数据是否允许为空，默认不能为空"""
        if not is_null and data or is_null:
            return data
        else:
            raise BaseException(f"{message}数据不能为空")

    def request_type_handler(self, headers=None):
        """通过headers判断请求类型"""
        if headers is None or 'Content-Type' not in headers.keys():
            return 'params'
        if 'application/json' in headers['Content-Type']:
            return 'json'
        elif 'application/form-data' in headers['Content-Type']:
            return 'params'
        elif 'application/x-www-form-urlencoded' in headers['Content-Type']:
            return 'data'
        else:
            return None

    def dataHandle_host(self, address):
        """解析地址映射配置文件的host参数并提取"""
        from common.utils import config
        host = address.split('.com')[0] + '.com'
        if config.info['gateway_host'] in host:
            return "${{gateway_host}}"
        elif config.info['lawyer_host'] in host:
            return "${{lawyer_host}}"
        elif config.info['callback_host'] in host:
            return "${{callback_host}}"
        else:
            raise BaseException(f"host: {host} ,配置文件没有对应的host参数")

    def dataHandle_url(self, address):
        """解析地址提取URL"""
        return address.split('.com')[-1]

    def dataHandler_is_run(self, is_run):
        if is_run and is_run == '是':
            return True
        elif is_run == '否':
            return False
        else:
            return None

    def write_yaml(self):

        # 1、循环遍历sheet，过滤test目录，并创建目录到data下（当有用例时创建）
        for sheet in self.get_sheet:  # sheet名称列表循环
            if 'test' not in sheet:
                module_list = []
                # 获取sheet页的所有数据 并遍历
                for i in self.excel_handle.get_sheet_data(sheetName=sheet):
                    # 把当前sheet的模块列表
                    if i['模块'] not in module_list:
                        module_list.append(i['模块'])
                        # 2、循环sheet内的excel数据
                ###1、按模块创建目录
                # print(module_list)
                for module in module_list:  # 模块列数据循环
                    # 1、创建模块目录
                    # E:\pythonProject\new\data\Sheet1\小法名律小程序
                    module_yaml_path = ensure_path_sep(f"{TESTDATA_DIR}{sheet}/{module}")
                    mk_dir(module_yaml_path)

                    ###2、分析excel数据
                    # 模块的所有数据
                    module_all_data = self.excel_handle.get_sheet_data(sheetName=sheet, moduleName=module)

                    # 获取当前模块的 功能列表
                    function_list = []
                    for module_data in module_all_data:
                        if module_data['功能'] not in function_list:
                            function_list.append(module_data['功能'])

                    # 功能列表数据 ['保存律师退订短信信息接口', '保存订单谈案关联信息']
                    for function_list_value in function_list:
                        # 当前功能列的所有数据集合
                        function_data = self.excel_handle.get_sheet_data(sheetName=sheet, funcName=function_list_value)

                        # yaml名称  auto_call_saveUnsubscribeReason
                        # 解析用例名称创建空的yaml文件
                        case = function_data[0]['用例名称'].split('test_')[-1]
                        if '_0' in case:
                            case = case.split('_0')[0]
                        case_path = f'{module_yaml_path}/{case}.yaml'
                        create_file(case_path)

                        #####1、通用公共数据(从功能列数据集合中取第一条数据)
                        case_common = {
                            "allureEpic": function_data[0]['版本号'],
                            "allureFeature": function_data[0]['模块'],
                            "allureStory": function_data[0]['功能']
                        }

                        case_data = {'case_common': case_common}

                        for function_data_value in function_data:
                            #####2、用例数据
                            # 1、基础信息数据
                            address = self.judge_is_null(function_data_value['请求地址'],
                                                         message=f"{function_data_value['功能']}的请求地址")
                            host = self.dataHandle_host(address)
                            url = self.dataHandle_url(address)
                            method = self.judge_is_null(function_data_value['请求方式'],
                                                        message=f"{function_data_value['功能']}的请求方式")
                            remark = self.judge_is_null(function_data_value['用例标题'], is_null=True)
                            is_run = self.dataHandler_is_run(function_data_value['是否运行'])
                            headers = self.dataHandle_dict(self.judge_is_null(function_data_value['请求头'],
                                                                              message=f"{function_data_value['功能']}的请求头"))
                            dependence = self.judge_is_null(function_data_value['依赖数据'], is_null=True)
                            request_type = self.request_type_handler(headers)
                            request_data = self.dataHandle_dict(
                                self.judge_is_null(function_data_value['请求参数'], is_null=True))

                            info_case = {
                                "host": host,
                                "url": url,
                                "method": method,
                                "remark": remark,
                                "is_run": is_run,
                                "headers": headers,
                                "requestType": request_type,
                                "requestData": request_data,
                                "dependence_case": None,
                                "dependence_case_data": None,
                                "sql_data": None,
                                "sql_assert": None,
                                "assert_data": None,
                                "process": {}
                            }
                            # 依赖数据处理
                            if dependence:
                                info_case['dependence_case'] = True
                                info_case['dependence_case_data'] = self.dataHandle_dict(dependence)

                            # 缺少不会入库 != ''兼容0的值
                            if function_data_value['数据库校验语句'] and function_data_value['数据库校验结果'] != '':
                                info_case['sql_data'] = function_data_value['数据库校验语句']
                                info_case['sql_assert'] = function_data_value['数据库校验结果']

                            # 2、校验数据
                            assert_data = {}
                            if status_code := function_data_value['校验状态码']:
                                assert_data["status_code"] = self.dataHandle_int(status_code)

                            # 检验字段集合
                            # ['$.code', '$.message']
                            assert_field_list = [function_data_value['校验字段1'], function_data_value['校验字段2']]
                            for key, assert_field in enumerate(assert_field_list):
                                if assert_field:
                                    assert_name = assert_field.split('.')[-1]
                                    assert_data[assert_name] = {
                                        "jsonpath": assert_field,
                                        "type": '==',
                                        "value": self.judge_is_null(function_data_value[f'校验内容{str(key + 1)}'],
                                                                    message=f"{function_data_value['功能']}的{assert_field}"),
                                        "AssertType": None,
                                        "message": self.judge_is_null(
                                            function_data_value[f'校验错误信息{str(key + 1)}'], is_null=True)
                                    }
                            if assert_data:
                                info_case['assert_data'] = assert_data

                            #######3、前后置数据
                            setup_execute_sql = function_data_value['前置条件(要执行的sql)']
                            setup_execute_request = function_data_value['前置条件(要执行的接口请求)']
                            teardown_execute_sql = function_data_value['后置条件(要执行的sql)']
                            teardown_to_params = function_data_value['后置条件(需要把响应参数拼接到sql)']

                            # 前置
                            setup_data = {}
                            if setup_execute_sql or setup_execute_request:
                                # 前置-执行sql处理
                                if setup_execute_sql := self.dataConvert(setup_execute_sql):
                                    setup_data['sql'] = setup_execute_sql
                                # 前置-执行请求处理
                                if request_data := self.dataConvert(setup_execute_request):
                                    setup_data['request'] = request_data

                            if setup_data:
                                info_case['process']['setup'] = setup_data

                            # 后置
                            teardown_data = {}
                            if teardown_execute_sql or teardown_to_params:
                                # 后置-执行sql处理
                                if teardown_execute_sql := self.dataConvert(teardown_execute_sql):
                                    teardown_data['sql'] = teardown_execute_sql
                                # 后置-需要把响应参数拼接到sql处理
                                if teardown_to_params := self.dataHandle_dict(teardown_to_params):
                                    teardown_data['is_params'] = teardown_to_params

                            if teardown_data:
                                info_case['process']['teardown'] = teardown_data

                            # 把info信息写入case中
                            case_data[function_data_value['用例名称'].split('test_')[-1]] = info_case

                        # 用case数据写入yaml文件中
                        YamlHandler(case_path).DictWriteYaml(case_data)


if __name__ == '__main__':
    # 读取excel文件生成yaml用例
    FromExcelWriteYaml().write_yaml()

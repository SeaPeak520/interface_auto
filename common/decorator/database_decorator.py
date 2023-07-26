import ast
import json
import os
from functools import wraps

from common.assertion.assert_control import AssertExecution
from common.log.log_control import LogHandler


def database_sql_assert(func):
    @wraps(func)
    def inner_wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if res and res.is_decorator:
            log = LogHandler(os.path.basename(__file__))
            _assert_result = None
            # 如果请求结果的code等于校验数据的code校验
            if json.loads(res.res_data)['code'] == res.yaml_assert_data['code']['value']:
                """处理 sql 参数 ：数据库校验"""
                from common.utils import config
                # 数据库校验开关
                if config.mysql.switch:
                    # 判断database_assert_sql的类型是否为list类型（excel读取是str类型，判断第一个字符是否为'['）,及 非空处理
                    if res.yaml_database_assert_sql and res.yaml_database_assert_sql[0] == '[' and \
                            res.yaml_database_assert_sql[-1] == ']':
                        database_assert_sql = ast.literal_eval(res.yaml_database_assert_sql)
                        database_assert_result = ast.literal_eval(res.yaml_database_assert_result)
                    else:
                        database_assert_sql = res.yaml_database_assert_sql
                        database_assert_result = res.yaml_database_assert_result

                    # 判断不为空才执行校验   assert_sql：可能为sql或None ；sql_assert：可能为0或1或None。 None不执行
                    if database_assert_sql and database_assert_result is not None:
                        _assert_result = AssertExecution().assert_execution(database_assert_sql, database_assert_result)
                else:
                    log.info("数据库校验已关闭，用例不进行数据库校验")
            res.res_assert_result = _assert_result
        return res

    return inner_wrapper

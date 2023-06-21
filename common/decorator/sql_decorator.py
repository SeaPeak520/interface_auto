import ast
import json
import os
from functools import wraps

from common.assertion.assert_control import AssertExecution
from common.log.log_control import LogHandler


def sql_assert(func):
    @wraps(func)
    def inner_wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        log = LogHandler(os.path.basename(__file__))

        _sql_result = None
        if json.loads(res.res_data)['code'] == res.yaml_assert_data['code']['value']:
            """处理 sql 参数 ：数据库校验"""
            from common.utils import config
            # 数据库校验开关
            if config.mysql['mysql_db_switch']:
                # 判断sql_data的类型是否为list类型（excel读取是str类型，判断第一个字符是否为'['）,及 非空处理
                if res.yaml_sql_data and res.yaml_sql_data[0] == '[' and res.yaml_sql_data[-1] == ']':
                    sql_data = ast.literal_eval(res.yaml_sql_data)
                    sql_expect_result = ast.literal_eval(res.yaml_sql_assert)
                else:
                    sql_data = res.yaml_sql_data
                    sql_expect_result = res.yaml_sql_assert

                # 判断不为空才执行校验   sql_data：可能为sql或None ；sql_assert：可能为0或1或None。 None不执行
                if sql_data and sql_expect_result is not None:
                    _sql_result = AssertExecution().assert_execution(sql_data, sql_expect_result)
            else:
                log.info(f"数据库校验已关闭，用例不进行数据库校验")
        res.res_sql_result = _sql_result
        return res

    return inner_wrapper

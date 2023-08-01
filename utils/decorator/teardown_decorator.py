import ast
import os
from functools import wraps

from utils.db.mysql_control import SqlHandler
from utils.log.log_control import LogHandler
from utils.requests.teardown_control import TearDownControl
from utils.other.regular_control import teardown_regular


def teardown_decorator(func):
    @wraps(func)
    def inner_wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if res and res.is_decorator:
            res_text = res.res_data
            res_yaml_assert_data = res.yaml_assert_data
            if any(i in 'code' for i in res_text.keys()) and any(i in 'code' for i in res_yaml_assert_data.keys()):
                res_code = res_text['code']
                yaml_code = res_yaml_assert_data['code']['value']
                # 判断接口不符合预期，不执行后置条件
                if res_code == yaml_code:
                    # 判断后置条件是否为空
                    if teardown_sql := res.yaml_data.teardown_sql:
                        m = SqlHandler()
                        _regular_data = teardown_regular(f"{teardown_sql}")
                        _regular_data = ast.literal_eval(_regular_data)
                        for i in _regular_data:
                            m.execution_by_sql_type(i)
                    if teardown := res.yaml_data.teardown:
                        TearDownControl(teardown).is_teardown()
                else:
                    log = LogHandler(os.path.basename(__file__))
                    log.error(f"{res.yaml_remark} 的code不一致，没有执行后置条件")
        return res

    return inner_wrapper

import json
import os
from functools import wraps

from common.db.mysql_control import SqlHandle
from common.log.log_control import LogHandler
from common.utils.file_control import get_value


def teardown_decorator(func):
    @wraps(func)
    def inner_wrapper(*args, **kwargs):
        res = func(*args, **kwargs)

        res_text = json.loads(res.res_data)
        res_yaml_assert_data = res.yaml_assert_data

        if any(i in 'code' for i in res_text.keys()) and any(i in 'code' for i in res_yaml_assert_data.keys()):
            res_code = res_text['code']
            yaml_code = res_yaml_assert_data['code']['value']
            if res_code == yaml_code:
                if any('teardown' in i for i in res.yaml_data.process.keys()):

                    teardown_data = res.yaml_data.process['teardown']
                    teardown_key_list = list(teardown_data.keys())
                    m = SqlHandle()

                    for teardown_key_value in teardown_key_list:
                        if 'sql' in teardown_key_value.lower():
                            if 'num' in teardown_key_value.lower():
                                m.data_type(teardown_data[teardown_key_value], state='num')
                            else:
                                m.data_type(teardown_data[teardown_key_value])

                        if 'is_params' in teardown_key_value.lower():
                            # 获取is_params下的所有key
                            is_params_list = list(teardown_data[teardown_key_value].keys())

                            for is_params_value in is_params_list:
                                # 获取接口返回值，转成字符串
                                is_params_key = str(get_value(json.loads(res.res_data), is_params_value)[0])
                                # value 和 接口返回值拼接
                                is_params_sql = teardown_data[teardown_key_value][is_params_value] + is_params_key
                                m.data_type(is_params_sql)
            else:
                log = LogHandler(os.path.basename(__file__))
                log.error(f"{res.yaml_remark} 的code不一致，没有执行后置条件")

        return res

    return inner_wrapper

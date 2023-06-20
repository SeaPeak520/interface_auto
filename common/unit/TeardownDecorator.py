import json
from functools import wraps
from common.db.MysqlHelper import SqlHandle
from common.utils.FileHelper import get_value


def teardown_decorator(func):
    @wraps(func)
    def inner_wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        
        if any('teardown' in i for i in res.yaml_data.process.keys()):
            
            teardown_data = res.yaml_data.process['teardown']
            teardown_key_list = list(teardown_data.keys())
            m =SqlHandle()

            for teardown_key_value in teardown_key_list:
                if 'sql' in teardown_key_value.lower():
                    if 'num' in teardown_key_value.lower():
                        m.data_type(teardown_data[teardown_key_value],state='num')
                    else:
                        m.data_type(teardown_data[teardown_key_value])
                
                if 'is_params' in teardown_key_value.lower():
                    #获取is_params下的所有key
                    is_params_list = list(teardown_data[teardown_key_value].keys())

                    for is_params_value in is_params_list:
                        #获取接口返回值，转成字符串
                        is_params_key = str(get_value(json.loads(res.res_data),is_params_value)[0])    
                        #value 和 接口返回值拼接
                        is_params_sql = teardown_data[teardown_key_value][is_params_value] + is_params_key
                        m.data_type(is_params_sql)
        return res

    return inner_wrapper

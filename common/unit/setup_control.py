from common.db.mysql_control import SqlHandler
from common.log.log_control import LogHandler
from common.unit.dependent_case import DependentCase


def request_type(headers=None):
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


def setup_handler(__yaml_case):
    """前置条件的数据处理"""
    # 如果process参数所有key不包含‘setup’，返回 None（全部为Ture才执行）
    if all('setup' not in i for i in __yaml_case.process.keys()):
        return None
    setup_data = __yaml_case.process['setup']
    setup_key_list = list(setup_data.keys())
    for data in setup_key_list:
        # 前置-sql数据处理
        if 'sql' in data.lower():
            s = SqlHandler()
            s.execution_by_sql_type(setup_data[data])
        # 前置-接口数据处理
        if 'request' in data.lower():
            m = LogHandler()
            for i in setup_data[data]:
                try:
                    _case_id = i['case_id']
                    _replace_key = i['replace_key']

                    res = DependentCase(__yaml_case).response_by_case_id(_case_id, _replace_key)

                    m.warning(f"{__yaml_case.remark} 前置请求：{_case_id} ，执行结果：{res}")
                except:
                    raise

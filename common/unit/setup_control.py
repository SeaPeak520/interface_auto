from common.db.mysql_control import SqlHandler
from common.exceptions.exceptions import ValueTypeError


def setup_handler(__yaml_case):
    """前置条件的数据处理"""
    setup_sql = __yaml_case.setup_sql

    if not setup_sql:
        return None
    else:
        s = SqlHandler()
        if isinstance(setup_sql, list):
            for i in setup_sql:
                s.execution_by_sql_type(i)
        elif isinstance(setup_sql, str) and setup_sql[0] != '[':
            s.execution_by_sql_type(setup_sql)
        else:
            raise ValueTypeError(f"传入数据类型不正确，接受的是list或str: {setup_sql}")

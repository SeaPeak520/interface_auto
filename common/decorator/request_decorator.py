from functools import wraps

from common.log.log_control import LogHandler


# 接口请求装饰器
def request_decorator(switch):
    def logging(func):
        @wraps(func)
        def inner_wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            # 判断日志为开启状态，才打印日志
            if res and res.is_decorator:
                log = LogHandler(res.file)
                # 判断日志开关为开启状态
                if switch:
                    _log_msg = f"\n======================================================\n" \
                               f"用例标题: {res.yaml_remark}\n" \
                               f"请求路径: {res.req_url}\n" \
                               f"请求方式: {res.req_method}\n" \
                               f"请求头:   {res.req_headers}\n" \
                               f"请求内容: {res.yaml_body}\n" \
                               f"接口响应内容: {res.res_data}\n" \
                               f"接口响应时长: {res.res_time} ms\n" \
                               f"数据库校验结果: {res.res_sql_result}\n" \
                               f"Http状态码: {res.res_status_code}\n" \
                               "====================================================="
                    log.info(_log_msg)
            return res
        return inner_wrapper
    return logging

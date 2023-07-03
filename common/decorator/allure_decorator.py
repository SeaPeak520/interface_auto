from functools import wraps

from common.allure.allure_tools import allure_step


def allure_decorator(func):
    @wraps(func)
    def inner_wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if res and res.is_decorator:
            # 添加allure步骤
            allure_step("请求URL: ", res.req_url)
            allure_step("请求方式: ", res.req_method)
            allure_step("请求头: ", str(res.req_headers))
            allure_step("请求数据: ", str(res.yaml_body))
            allure_step("数据库校验结果: ", res.res_assert_result)
            allure_step("响应断言数据: ", str(res.yaml_assert_data))
            allure_step("响应耗时(ms): ", str(res.res_time))
            allure_step("响应结果: ", res.res_data)
        return res

    return inner_wrapper

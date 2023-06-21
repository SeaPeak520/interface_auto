from functools import wraps

from common.assertion.assert_control import AssertUtil


def assert_decorator(func):
    @wraps(func)
    def inner_wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        AssertUtil(assert_data=res.yaml_assert_data,
                   request_data=res.yaml_body,
                   response_data=res.res_data,
                   status_code=res.res_status_code,
                   remark=res.yaml_remark).assert_type_handle()
        return res

    return inner_wrapper

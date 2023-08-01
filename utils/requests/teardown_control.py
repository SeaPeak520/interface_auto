import ast
import os
from typing import Text, Dict

from utils.log.log_control import LogHandler
from utils.cache.cache_control import CacheHandler
from utils.other.regular_control import config_regular


class TearDownControl:
    """ 处理依赖相关的业务 """

    def __init__(self, teardown_data):
        self.__data = teardown_data
        self.log = LogHandler(os.path.basename(__file__))

    @classmethod
    def get_cache(cls, case_id: Text) -> Dict:
        """
        获取缓存用例池中的数据，通过 case_id 提取
        :param case_id:
        :return: case_id_01
        """
        return CacheHandler.get_cache(case_id)

    def response_by_case_id(self, case_id, replace_key) -> dict:
        """通过 case_id 获取用例，然后用_replace_key替换请求参数，最后进行接口请求并返回"""
        from utils.requests.RequestSend import RequestSend
        # 判断依赖数据类型，
        re_data = config_regular(str(self.get_cache(case_id)))
        # 把str类型转成字典
        _re_data = ast.literal_eval(re_data)

        # 替换依赖接口的请求参数值
        if replace_key:
            for r, k in replace_key.items():
                r_list = r.split('_')
                r_len = len(r_list)
                if r_len == 1:
                    _re_data['requestData'][r_list[r_len - 1]] = k
                elif r_len == 2:
                    _re_data['requestData'][r_list[r_len - 2]][r_list[r_len - 1]] = k
                elif r_len == 3:
                    _re_data['requestData'][r_list[r_len - 3]][r_list[r_len - 2]][r_list[r_len - 1]] = k
                else:
                    raise ValueError(f"{replace_key} 格式不规范，请检查！")
        # 执行请求
        res = RequestSend(_re_data).http_request(is_decorator=False)
        self.log.warning(f"后置接口执行，响应状态码{res.res_status_code}  请求数据：{res}")

    def is_teardown(self) -> None:
        """
        :return:
        """
        # 获取用例中的dependent_type值，判断该用例是否需要执行依赖
        for i in self.__data:
            self.response_by_case_id(i.case_id,i.replace_key)


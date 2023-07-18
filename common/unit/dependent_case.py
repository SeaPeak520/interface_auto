import ast
import json
import os
from typing import Text, Dict, Union

from common.exceptions.exceptions import ValueNotFoundError, ValueTypeError
from common.log.log_control import LogHandler
from common.utils.cache_control import CacheHandler
from common.utils.file_control import get_value
from common.utils.models import TestCase, DependentData, DependentType
from common.utils.regular_control import cache_regular, config_regular


class DependentCase:
    """ 处理依赖相关的业务 """

    def __init__(self, dependent_yaml_case):
        self.__yaml_case = dependent_yaml_case
        self.log = LogHandler(os.path.basename(__file__))

    @classmethod
    def get_cache(cls, case_id: Text) -> Dict:
        """
        获取缓存用例池中的数据，通过 case_id 提取
        :param case_id:
        :return: case_id_01
        """
        return CacheHandler.get_cache(case_id)

    @classmethod
    def set_cache_value(cls, dependent_data: "DependentData") -> Union[Text, None]:
        """
        获取依赖中是否需要将数据存入缓存中
        """
        try:
            return dependent_data.set_cache
        except KeyError:
            return None

    def response_by_case_id(self, case_id, replace_key) -> dict:
        """通过 case_id 获取用例，然后用_replace_key替换请求参数，最后进行接口请求并返回"""
        from common.unit.RequestSend import RequestSend
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
        self.log.warning(res)

        return json.loads(res.res_data)

    @classmethod
    def replace_key(cls, dependent_data: "DependentData") -> dict:
        """ 获取需要替换的内容 """
        try:
            return dependent_data.replace_key
        except KeyError:
            return None

    @staticmethod
    def cache_by_sql(dependent_sql, set_cache):
        """
        执行_dependent_sql，设置缓存，key为_set_cache，value为sql执行结果
        :param dependent_sql:
        :param set_cache:
        :return:
        """
        from common.db.mysql_control import MysqlDB
        m = MysqlDB()
        if sql_data := m.select(dependent_sql, state='one'):
            sql_data = sql_data[0]
        else:
            sql_data = None
        if set_cache is not None:
            CacheHandler.update_cache(cache_name=set_cache, value=sql_data)

    def _dependent_type_for_sql(
            self,
            dependent_data: "DependentData") -> None:
        """
        判断依赖类型为 sql，程序中的依赖参数从 数据库中提取数据
        @param setup_sql: 前置sql语句
        @param dependence_case_data: 依赖的数据
        @param jsonpath_dates: 依赖相关的用例数据
        @return:
        """
        # 判断依赖数据类型，依赖 sql中的数据
        _dependent_sql = dependent_data.dependent_sql  # list or str or None
        _set_cache = self.set_cache_value(dependent_data)  # list or str or None
        if not _dependent_sql:
            raise ValueError("关联sql数据为空，请检查！")
        if isinstance(_dependent_sql, list) and isinstance(_set_cache, list) and len(_set_cache) == len(_dependent_sql):
            for k, v in enumerate(_dependent_sql):
                self.cache_by_sql(v, _set_cache[k])
        elif isinstance(_dependent_sql, str) and isinstance(_set_cache, str):
            self.cache_by_sql(_dependent_sql, _set_cache)
        else:
            raise ValueTypeError(f"传入数据类型不正确，接受的是list或str: {_dependent_sql}, {_set_cache}")

    def is_dependent(self) -> None:
        """
        判断是否有数据依赖
        :return:
        """
        # 获取用例中的dependent_type值，判断该用例是否需要执行依赖
        _dependent_type = self.__yaml_case.dependence_case
        # 判断是否有依赖
        if _dependent_type is True:
            # 获取依赖用例数据
            _dependence_case_dates = self.__yaml_case.dependence_case_data
            # 循环所有需要依赖的数据
            try:
                for dependence_case_data in _dependence_case_dates:
                    # case_id='caseCollectConcel' dependent_data=[DependentData(dependent_type='response', jsonpath='$.code', set_cache='login_02_v_code'), DependentData(dependent_type='response', jsonpath='$.message', set_cache='login_02_v_message')]
                    # case_id='self' dependent_data=[DependentData(dependent_type='sqlData', jsonpath='$.code', set_cache='login_02_v_code')]
                    _case_id = dependence_case_data.case_id  # 依赖用例
                    dependent_data = dependence_case_data.dependent_data
                    # 判断依赖数据为sql，case_id需要写成self，否则程序中无法获取case_id
                    if _case_id == 'self':
                        for i in dependent_data:
                            self._dependent_type_for_sql(
                                dependent_data=i)
                    elif dependent_data is not None:
                        for i in dependent_data:
                            if i.dependent_type == DependentType.RESPONSE.value:
                                # 获取dependent_data中set_cache的值
                                _set_cache = self.set_cache_value(i)
                                # 获取dependent_data中set_cache的值  list
                                _replace_key = self.replace_key(i)

                                _jsonpath = i.jsonpath

                                res = self.response_by_case_id(_case_id, _replace_key)

                                if isinstance(_set_cache, list) and isinstance(_jsonpath, list) and len(
                                        _set_cache) == len(_jsonpath):
                                    for k, v in enumerate(_set_cache):
                                        # 从res通过jsonpath获取结果
                                        _set_value = get_value(res, _jsonpath[k])[0]
                                        CacheHandler.update_cache(cache_name=v, value=_set_value)
                                elif isinstance(_set_cache, str) and isinstance(_jsonpath, str):
                                    _set_value = get_value(res, _jsonpath)[0]
                                    CacheHandler.update_cache(cache_name=_set_cache, value=_set_value)
                                else:
                                    raise ValueTypeError(
                                        f"传入数据类型不正确，接受的是list或str: _jsonpath: {_set_cache}, _jsonpath: {_jsonpath}")
                            # sqlData
                            elif i.dependent_type == DependentType.SQL_DATA.value:
                                _replace_key = self.replace_key(i)
                                self.response_by_case_id(_case_id, _replace_key)
                                self._dependent_type_for_sql(
                                    dependent_data=i)
                            # request 只请求
                            elif i.dependent_type == DependentType.REQUEST.value:
                                _replace_key = self.replace_key(i)
                                self.response_by_case_id(_case_id, _replace_key)
                            else:
                                raise ValueError(
                                    "依赖的dependent_type不正确，只支持request、response、sql依赖\n"
                                    f"当前填写内容: {i.dependent_type}"
                                )
            except KeyError as exc:
                raise ValueNotFoundError(
                    f"dependence_case_data依赖用例中，未找到 {exc} 参数，请检查是否填写"
                    f"如已填写，请检查是否存在yaml缩进问题"
                ) from exc
            except TypeError as exc:
                raise ValueNotFoundError(
                    "dependence_case_data下的所有内容均不能为空！"
                    "请检查相关数据是否填写，如已填写，请检查缩进问题"
                ) from exc

    def get_dependent_data(self) -> "TestCase":
        """
        :return:
        """
        self.is_dependent()
        _regular_data = cache_regular(f"{self.__yaml_case.dict()}")
        _regular_data = ast.literal_eval(_regular_data)
        return TestCase(**_regular_data)


if __name__ == '__main__':
    from common.config import TESTDATA_DIR
    from common.file_tools.get_yaml_data_analysis import CaseData

    a = []
    file = f'{TESTDATA_DIR}xiaofa/案源收藏/caseCollectAdd.yaml'
    case_data = CaseData(file).case_process(case_id_switch=True)
    case_data = case_data[0]['caseCollectAdd']
    print(json.dumps(case_data))
    __yaml_case = TestCase(**case_data)
    print(__yaml_case)
    # DependentCase(__yaml_case).get_dependent_data()

    # print(json.dumps(case_data[0], ensure_ascii=False))

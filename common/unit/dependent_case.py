import ast
import json
import os
from typing import Text, Dict, Union

from common.exceptions.exceptions import ValueNotFoundError
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
        _case_data = CacheHandler.get_cache(case_id)
        return _case_data

    @classmethod
    def set_cache_value(cls, dependent_data: "DependentData") -> Union[Text, None]:
        """
        获取依赖中是否需要将数据存入缓存中
        """
        try:
            return dependent_data.set_cache
        except KeyError:
            return None

    @classmethod
    def replace_key(cls, dependent_data: "DependentData"):
        """ 获取需要替换的内容 """
        try:
            _replace_key = dependent_data.replace_key
            return _replace_key
        except KeyError:
            return None

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
        from common.db.mysql_control import MysqlDB
        m = MysqlDB()
        sql_data = m.select(dependent_data.dependent_sql, state='one')[0]
        _set_cache = self.set_cache_value(dependent_data)
        if _set_cache is not None:
            CacheHandler.update_cache(cache_name=_set_cache, value=sql_data)

    def is_dependent(self) -> None:
        """
        判断是否有数据依赖
        :return:
        """

        # 获取用例中的dependent_type值，判断该用例是否需要执行依赖
        _dependent_type = self.__yaml_case.dependence_case
        # 获取依赖用例数据
        _dependence_case_dates = self.__yaml_case.dependence_case_data

        # _setup_sql = self.__yaml_case.setup_sql
        # 判断是否有依赖
        if _dependent_type is True:
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
                    else:
                        if dependent_data is not None:
                            for i in dependent_data:
                                from common.unit.RequestSend import RequestSend
                                if i.dependent_type in (DependentType.RESPONSE.value, DependentType.SQL_DATA.value):
                                    # 获取dependent_data中set_cache的值
                                    _set_cache = self.set_cache_value(i)
                                    # 获取dependent_data中set_cache的值  list
                                    _replace_key = self.replace_key(i)

                                    # 判断依赖数据类型，
                                    re_data = config_regular(str(self.get_cache(_case_id)))
                                    # 把str类型转成字典
                                    re_data = ast.literal_eval(re_data)

                                    # 替换依赖接口的请求参数值
                                    if _replace_key:
                                        for r, k in _replace_key.items():
                                            re_data['requestData'][r] = k

                                    # 执行请求
                                    res = RequestSend(re_data).http_request(dependence=True).res_data
                                    # 转换类型
                                    res = json.loads(res)
                                    # response
                                    if i.dependent_type == DependentType.RESPONSE.value:
                                        _set_value = get_value(res, i.jsonpath)[0]
                                        CacheHandler.update_cache(cache_name=_set_cache, value=_set_value)
                                    # sqlData
                                    else:
                                        self._dependent_type_for_sql(
                                            dependent_data=i)
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
        jsonpath 和 依赖的数据,进行替换
        :return:
        """
        self.is_dependent()
        _regular_data = cache_regular(f"{self.__yaml_case.dict()}")
        _regular_data = ast.literal_eval(_regular_data)
        _new_data = TestCase(**_regular_data)
        return _new_data


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

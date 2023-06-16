#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common.config import TESTDATA_DIR
from common.utils.ReadYaml import get_all_caseyaml
from common.file_tools.get_yaml_data_analysis import CaseData
from common.utils.cache_control import CacheHandler, _cache_config
def write_case_process():
    """
    获取所有用例，写入用例池中
    :return:
    """
    # 循环拿到所有存放用例的文件路径
    for i in get_all_caseyaml(TESTDATA_DIR):
        #print(i)
        # 循环读取文件中的数据
        case_process = CaseData(i).case_process(case_id_switch=True)
        if case_process is not None:
            # 转换数据类型
            for case in case_process:
                for k, v in case.items():
                    # 判断 case_id 是否已存在
                    case_id_exit = k in _cache_config.keys()
                    # 如果case_id 不存在，则将用例写入缓存池中
                    if not case_id_exit:
                        CacheHandler.update_cache(cache_name=k, value=v)
                        # case_data[k] = v
                    else:
                        raise ValueError(f"case_id: {k} 存在重复项, 请修改case_id\n"
                                         f"文件路径: {i}")

write_case_process()

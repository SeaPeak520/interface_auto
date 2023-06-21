import json
import os
import sys

sys.path.append(os.path.dirname(sys.path[0]))

class JsonHandle:
    def __init__(self,file):
        self.file = file
        if not os.path.isfile(self.file):
            raise FileNotFoundError(f"{self.file}文件不存在")

    # 获取json文件的内容，返回dict格式
    def get_json_data(self) -> dict[str, str | dict]:
        """
        :param dataFile: json文件路径
        :return:
        """
        with open(self.file, "r", encoding='utf-8') as f:
            # 先读取文件中字符串到str_f，再用json.loads(str_f)函数把字符串转换为数据结构
            str_f = f.read()
            dic = json.loads(str_f) if len(str_f) > 0 else {}
        f.close()
        return dic

    # 设置json文件，dic的键存在于dataFile中则替换值，不存在则新增键值
    def set_json_data(self, dic: dict) -> None:
        """
        :param dataFile: json文件路径
        :param dic: 匹配内容：存在则替换，不存在则新建,拿两个dict数据比较
        :return:
        """
        fir = self.get_json_data()  # 文件的
        sec = dic  # 接口获取的

        fir_keylist = set(fir.keys())  # 文件的key集合
        sec_keylist = set(sec.keys())  # 接口的key集合

        for sec_key in sec_keylist:  # 循环接口的key集合
            # 如果接口获取的key在文件的key集合里,执行
            # 如果接口获取的key不在文件的key集合里，则新增对应的keyvalue
            if (
                sec_key in fir_keylist
                and fir[sec_key] != sec[sec_key]
                or sec_key not in fir_keylist
            ):  # 则判断对应key的value是否相同
                fir[sec_key] = sec[sec_key]

        with open(self.file, "w+", encoding='utf-8') as f:
            json.dump(fir, f)
            f.close()


if __name__ == '__main__':
    # 用法
    from common.config import TESTDATA_DIR
    path = f'{TESTDATA_DIR}token.json'
    jh = JsonHandle(path)
    json_data = jh.get_json_data()
    print(json_data)
    # print(json_data.keys())

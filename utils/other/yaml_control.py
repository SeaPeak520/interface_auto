import ast
import os
import sys

import yaml

from common.config.setting import ensure_path_sep
from utils.other.regular_control import config_regular

sys.path.append(os.path.dirname(sys.path[0]))


class YamlHandler:
    def __init__(self, file: str):
        self.file = file
        if not os.path.isfile(self.file):
            raise FileNotFoundError(f"{self.file}文件不存在")

    # 获取yaml文件的单个数据
    def get_yaml_data(self) -> dict[str, str | dict]:
        """
        :return: 文件的dict数据
        """
        with open(self.file, 'r', encoding='utf-8') as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    def update_yaml_data(self, key, value):
        """
        读取yaml全量数据（yaml.load方式），更改，再全量写入文件中
        更新yaml文件中的数据，采用key_value方式
        ("case_common:allureEpic", 'v1222')
        :param key: "case_common:allureEpic"
        :param value: 'v1222'
        :return:
        """
        # 读取yaml文件，返回字典数据
        with open(self.file, 'r') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)

        # 更新字典值
        key_list = key.split(':')
        key_len = len(key_list)

        if key_len == 1:
            data[key_list[0]] = value
        elif key_len == 2:
            data[key_list[0]][key_list[1]] = value
        elif key_len == 3:
            data[key_list[0]][key_list[1]][key_list[2]] = value
        elif key_len == 4:
            data[key_list[0]][key_list[1]][key_list[2]][key_list[3]] = value
        else:
            raise ValueError(f"暂不支持格式，应为'a_b_c_d'之内：{key}")

        # # 将字典数据转换回YAML格式并写入文件
        with open(self.file, 'w') as file:
            yaml.safe_dump(data, file, default_flow_style=False, sort_keys=False, encoding='utf-8', allow_unicode=True)

    def set_write_yaml_data(self, key: str, value) -> int:
        """
        读取yaml全量数据（以行读取），更改行数据，再全量写入文件中
        更改 yaml 文件中的值, 并且保留注释内容 {'case_common': {'allureEpic': 'V2.1'}}
        :param key: 字典的key   文本匹配allureEpic
        :param value: 写入的值  V1.1
        :return:
        """
        with open(self.file, 'r', encoding='utf-8') as file:
            lines = [line for line in file.readlines() if line != '\n']
            file.close()

        with open(self.file, 'w', encoding='utf-8') as file:
            flag = 0
            for line in lines:
                # allureEpic
                left_str = line.split(":")[0]
                if key == left_str.lstrip() and '#' not in line:
                    newline = f"{left_str}: {value}"
                    file.write(f'{newline}\n')
                    flag = 1
                else:
                    file.write(f'{line}')
            file.close()
            return flag

    def write_yaml_by_dict(self, dict_data):
        # 不添加则会写入null，作用：把None不写入值
        def represent_none(self, _):
            return self.represent_scalar('tag:yaml.org,2002:null', '')

        yaml.add_representer(type(None), represent_none, Dumper=yaml.SafeDumper)
        """把dict数据全量写入到yaml文件中"""
        with open(self.file, 'w+', encoding='utf-8') as f:
            yaml.safe_dump(dict_data, f, default_flow_style=False, sort_keys=False, encoding='utf-8',
                           allow_unicode=True)


# 获取单个yaml文件的测试数据
class GetYamlCaseData(YamlHandler):
    """ 获取测试用例中的数据 """

    def get_yaml_case_data(self):
        """
        获取正则处理过的测试用例数据
        :return:
        """
        _yaml_data = self.get_yaml_data()
        # 正则处理yaml文件中的数据
        re_data = config_regular(str(_yaml_data))
        return ast.literal_eval(re_data)


# 获取某个目录下的所有yaml文件的路径
def get_all_caseyaml(file_path, is_yaml=True):
    yamlfile_path = []
    # 过滤掉在file_path中文件或目录
    target_list = ['pre', 'test.yaml', 'test_bbak.yaml', 'token.json']
    for name in os.listdir(file_path):  # ['Collect', 'pre', 'test1.yaml', 'test_bbak.yaml', 'token.json', 'UserInfo']
        if name not in target_list:
            # 获取yaml测试文件
            if is_yaml:
                if name.endswith('.yaml'):
                    yamlfile_path.append(os.path.join(file_path, name))
                else:
                    for root, dirs, files in os.walk(os.path.join(file_path, name)):
                        for _file_path in files:
                            path = os.path.join(root, _file_path)
                            yamlfile_path.append(ensure_path_sep(path))
            # 获取allure报告的test-cases
            else:
                yamlfile_path.append(os.path.join(file_path, name))
    return yamlfile_path


if __name__ == '__main__':
    # 用法
    from common.config import TESTDATA_DIR

    path = f'{TESTDATA_DIR}xiaofa/案源收藏/caseCollectAdd.yaml'

    a = GetYamlCaseData(path).get_yaml_case_data()
    print(type(a['caseCollectAdd']['requestData']))

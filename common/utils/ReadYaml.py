import ast
import yaml
import os
import sys
from common.utils.DirHelper import ensure_path_sep
from common.utils.regularHandle import regular
sys.path.append(os.path.dirname(sys.path[0]))

class YamlHandler:
    def __init__(self, file: str):
        self.file = file
        if not os.path.isfile(self.file):
            raise FileNotFoundError(f"{self.file}文件不存在")

    # 获取yaml文件的单个数据
    def get_yaml_data(self) -> dict[str, str | dict]:
        """
        :param dataFile: 文件路径
        :return: 文件的dict数据
        """
        with open(self.file, 'r', encoding='utf-8') as f:
            return yaml.load(f, Loader=yaml.FullLoader)

    def update_dict(self,key,value):
        """更新yaml文件中的数据，采用key_value方式
        ("case_common:allureEpic", 'v1222')
        :param key: "case_common:allureEpic"
        :param value: 'v1222'
        :return:
        """
        #读取yaml文件，返回字典数据
        with open(self.file, 'r') as file:
            data = yaml.load(file, Loader=yaml.FullLoader)

        #更新字典值
        key_list = key.split(':')
        key_len = len(key_list)

        if key_len ==1:
            data[key_list[0]] = value
        if key_len == 2:
            data[key_list[0]][key_list[1]] = value
        if key_len == 3:
            data[key_list[0]][key_list[1]][key_list[2]] = value
        if key_len == 4:
            data[key_list[0]][key_list[1]][key_list[2]][key_list[3]] = value

        # # 将字典数据转换回YAML格式并写入文件
        with open(self.file, 'w') as file:
            yaml.safe_dump(data,file, default_flow_style=False, sort_keys=False, encoding='utf-8', allow_unicode=True)

    def write_yaml_data(self, key: str, value) -> int:
        """
        更改 yaml 文件中的值, 并且保留注释内容 {'case_common': {'allureEpic': 'V2.1'}}
        :param key: 字典的key   allureEpic
        :param value: 写入的值  V1.1
        :return:
        """
        with open(self.file, 'r', encoding='utf-8') as file:
            lines = [line for line in file.readlines() if line != '\n']
            file.close()

        with open(self.file, 'w', encoding='utf-8') as file:
            flag = 0
            for line in lines:
                #allureEpic
                left_str = line.split(":")[0]
                if key == left_str.lstrip() and '#' not in line:
                    newline = f"{left_str}: {value}"
                    file.write(f'{newline}\n')
                    flag = 1
                else:
                    file.write(f'{line}')
            file.close()
            return flag

    def DictWriteYaml(self,dict_data):
        """把dict数据全量写入到yaml文件中"""
        with open(self.file,'w+',encoding='utf-8') as f:
            yaml.safe_dump(dict_data,f, default_flow_style=False, sort_keys=False, encoding='utf-8', allow_unicode=True)

#获取单个yaml文件的测试数据
class GetYamlCaseData(YamlHandler):
    """ 获取测试用例中的数据 """
    def get_yaml_case_data(self):
        """
        获取正则处理过的测试用例数据
        :return:
        """
        _yaml_data = self.get_yaml_data()
        # 正则处理yaml文件中的数据
        re_data = regular(str(_yaml_data))
        return ast.literal_eval(re_data)


#获取某个目录下的所有yaml文件的路径
def get_all_caseyaml(file_path):
    yamlfile_path = []
    #过滤掉在file_path中文件或目录
    target_list = ['pre', 'test.yaml', 'test_bbak.yaml', 'token.json']  
    for name in os.listdir(file_path):  #['Collect', 'pre', 'test1.yaml', 'test_bbak.yaml', 'token.json', 'UserInfo']
        if name not in target_list:
            if name.endswith('.yaml'):
                yamlfile_path.append(os.path.join(file_path, name))
            else:
                for root, dirs, files in os.walk(os.path.join(file_path, name)):
                    for _file_path in files:
                        path = os.path.join(root, _file_path)
                        yamlfile_path.append(ensure_path_sep(path))
    return yamlfile_path


if __name__ == '__main__':
    # 用法
    from common.config import TESTDATA_DIR

    path = f'{TESTDATA_DIR}xiaofa/案源收藏/caseCollectAdd.yaml'

    a = GetYamlCaseData(path).get_yaml_case_data()
    print(a)
    #b = YamlHandler(path)
    #b.write_yaml_data("allureEpic",'v1.2')
    #b.update_dict("case_common:allureEpic", 'v1222')



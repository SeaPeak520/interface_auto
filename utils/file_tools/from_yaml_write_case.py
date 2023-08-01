import ast
import os
import re
import shutil

from common.config import TESTDATA_DIR, TEMPLATE_FILE, TESTCASE_DIR
from utils.log.log_control import LogHandler
from utils.other.dir_control import mk_dir
from common.config.setting import ensure_path_sep
from utils.other.file_control import alter_file_content
from utils.other.yaml_control import get_all_caseyaml, YamlHandler


# 读取yaml文件写入用例
def write_testcase():
    log = LogHandler(os.path.basename(__file__))
    # 获取测试数据目录的所有yaml文件路径list
    yaml_file_list = get_all_caseyaml(TESTDATA_DIR)
    # 遍历list
    for yaml_file in yaml_file_list:
        # yaml文件的名称  #caseCollectAdd
        yaml_file_name = os.path.basename(yaml_file).split('.yaml')[0]
        # 获取yaml文件所在的目录  #E:\pythonProject\new\data\Sheet4\案源收藏
        yaml_file_dir = ensure_path_sep(os.path.dirname(yaml_file))
        # test文件的目录 #E:/pythonProject/new/test_case/Sheet4\案源收藏
        case_file_dir = TESTCASE_DIR + yaml_file_dir.split(ensure_path_sep(TESTDATA_DIR))[-1]
        # test文件的路径 #E:/pythonProject/new/test_case/Sheet4\案源收藏/test_caseCollectAdd.py
        case_file_path = ensure_path_sep(f'{case_file_dir}/test_{yaml_file_name}.py')

        # 获取yaml文件数据
        yaml_data = YamlHandler(yaml_file).get_yaml_data()
        #执行的用例list
        case_list = list(yaml_data.keys())
        case_list.remove("case_common")
        
        #用例不存在执行
        if not os.path.exists(case_file_path):
            # 如果目录不存在，复制文件会报错
            if not os.path.isdir(case_file_dir):
                mk_dir(case_file_dir)
            # 复制模板文件并改名为用例名称
            shutil.copyfile(TEMPLATE_FILE, case_file_path)

            # 用例的类名
            class_name = f'Test_{yaml_file_name}'

            # test_case = re.split(r'(?=[A-Z])',yamlfile_name)
            # 把yaml名称用‘_’分割，转换成小写拼接成 函数名称
            test_case = re.split('_', yaml_file_name)
            function_name = 'test_' + '_'.join([x.lower() for x in test_case])

            alter_file_content(case_file_path, 'case_list', str(case_list))
            alter_file_content(case_file_path, 'allureEpic', yaml_data['case_common']['allureEpic'])
            alter_file_content(case_file_path, 'allureFeature', yaml_data['case_common']['allureFeature'])
            alter_file_content(case_file_path, 'class_name', class_name)
            alter_file_content(case_file_path, 'allureStory', yaml_data['case_common']['allureStory'])
            alter_file_content(case_file_path, 'function_name', function_name)

            log.info(f'新增用例：{case_file_path}')
        
        else:
            #如果test文件存在，则判断test文件和yaml文件的用例是否一致
            with open(case_file_path, 'r') as f:
                lines = f.readlines()
                line = lines[11][10:]
                line_list = ast.literal_eval(line)
                if case_list != line_list:
                    alter_file_content(case_file_path, str(line_list), str(case_list))
                    log.info(f'更新用例数：由 {case_list} 变更为 {line_list}')

if __name__ == '__main__':
    write_testcase()

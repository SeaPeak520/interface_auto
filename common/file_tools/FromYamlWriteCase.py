import os
import re
import shutil

from common.utils.ReadYaml import get_all_caseyaml, YamlHandler
from common.config import TESTDATA_DIR, TEMPLATE_FILE, TESTCASE_DIR
from common.utils.DirHelper import ensure_path_sep,mk_dir
from common.utils.FileHelper import alter_file_content
from common.log.LogHandler import LogHandler

# 读取yaml文件写入用例
def WriteTestCase():
    log =LogHandler(os.path.basename(__file__))
    #获取测试数据目录的所有yaml文件路径list
    yamlfile_list = get_all_caseyaml(TESTDATA_DIR)
    #遍历list
    for yamlfile in yamlfile_list:
        #yaml文件的名称  #caseCollectAdd
        yamlfile_name = os.path.basename(yamlfile).split('.yaml')[0]  
        #获取yaml文件所在的目录  #E:\pythonProject\new\data\Sheet4\案源收藏
        yamlfile_dir = ensure_path_sep(os.path.dirname(yamlfile))  
        #test文件的目录 #E:/pythonProject/new/test_case/Sheet4\案源收藏
        casefile_dir = TESTCASE_DIR + yamlfile_dir.split(ensure_path_sep(TESTDATA_DIR))[-1]  
        #test文件的路径 #E:/pythonProject/new/test_case/Sheet4\案源收藏/test_caseCollectAdd.py
        casefile_path = ensure_path_sep(f'{casefile_dir}/test_{yamlfile_name}.py')

        #获取yaml文件数据
        yaml_data = YamlHandler(yamlfile).get_yaml_data()
        #执行的用例list
        case_list = list(yaml_data.keys())
        case_list.remove("case_common")
        
        #用例不存在执行
        if not os.path.exists(casefile_path):
            #如果目录不存在，复制文件会报错
            if not os.path.isdir(casefile_dir):
                mk_dir(casefile_dir)
            # 复制模板文件并改名为用例名称
            shutil.copyfile(TEMPLATE_FILE, casefile_path)  
            
            #用例的类名
            class_name = f'Test_{yamlfile_name}'
            
            #test_case = re.split(r'(?=[A-Z])',yamlfile_name)
            #把yaml名称用‘_’分割，转换成小写拼接成 函数名称
            test_case = re.split('_',yamlfile_name)
            function_name = 'test_' + '_'.join([x.lower() for x in test_case])

            alter_file_content(casefile_path, 'case_list', str(case_list))
            alter_file_content(casefile_path, 'allureEpic', yaml_data['case_common']['allureEpic'])
            alter_file_content(casefile_path, 'allureFeature', yaml_data['case_common']['allureFeature'])
            alter_file_content(casefile_path, 'class_name',  class_name)
            alter_file_content(casefile_path, 'allureStory', yaml_data['case_common']['allureStory'])
            alter_file_content(casefile_path, 'function_name', function_name)
            
            log.info(f'新增用例：{casefile_path}')
        
        else:
            #如果test文件存在，则判断test文件和yaml文件的用例是否一致
            with open(casefile_path, 'r') as f:
                lines = f.readlines()
                line = lines[10][10:]
                line_list = eval(line)
                if case_list != line_list:
                    alter_file_content(casefile_path, str(line_list), str(case_list))
                    log.info(f'更新用例数：由 {case_list} 变更为 {line_list}')

if __name__ == '__main__': 
    WriteTestCase()

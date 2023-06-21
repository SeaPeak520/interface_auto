import os
import sys

sys.path.append(os.path.dirname(sys.path[0]))

# 主目录
ROOT_DIR = str(os.path.realpath(__file__)).split('common\config')[0].replace('\\', '/')

# 测试用例目录
TESTCASE_DIR = f'{ROOT_DIR}test_case/'

# 测试数据目录
TESTDATA_DIR = f'{ROOT_DIR}data/'

# 前置测试数据的目录
PRE_DATA_DIR = f'{ROOT_DIR}data/pre/'

#缓存目录
CACHE_DIR = f'{ROOT_DIR}cache/'

# 配置文件目录
CONFIG_DIR = f'{ROOT_DIR}common/config/'

# 测试数据文件
TESTDATA_FILE = f'{TESTDATA_DIR}testdata.xlsx'

# cookie文件
COOKIE_FILE = f'{TESTDATA_DIR}cookie.txt'

# 测试用例模板文件
TEMPLATE_FILE = f'{CONFIG_DIR}testcase_template.py'

# token文件
TOKEN_FILE = f'{TESTDATA_DIR}token.json'



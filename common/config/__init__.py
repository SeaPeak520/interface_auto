from common.config.setting import root_path,ensure_path_sep

# 主目录
ROOT_DIR = root_path()

# 测试用例目录
TESTCASE_DIR = ensure_path_sep(f'{ROOT_DIR}/test_case/')

# 测试数据目录
TESTDATA_DIR = ensure_path_sep(f'{ROOT_DIR}/data/')

# 前置测试数据的目录
PRE_DATA_DIR = ensure_path_sep(f'{ROOT_DIR}/data/pre/')

# 缓存目录
CACHE_DIR = ensure_path_sep(f'{ROOT_DIR}/cache/')

# 配置文件目录
CONFIG_DIR = ensure_path_sep(f'{ROOT_DIR}/common/config/')


# 测试数据文件
TESTDATA_FILE = ensure_path_sep(f'{TESTDATA_DIR}testdata.xlsx')

# cookie文件
COOKIE_FILE = ensure_path_sep(f'{TESTDATA_DIR}cookie.txt')

# 测试用例模板文件
TEMPLATE_FILE = ensure_path_sep(f'{CONFIG_DIR}testcase_template.py')

#yaml配置文件
YAML_FILE = ensure_path_sep(f"{CONFIG_DIR}config.yaml")

# token文件
TOKEN_FILE = ensure_path_sep(f'{TESTDATA_DIR}token.json')

ALLURE_DIR = ensure_path_sep(f'{ROOT_DIR}/report/allure_report/')

ALLURE_TESTCASES = ensure_path_sep(f'{ALLURE_DIR}data/test-cases/')

ALLURE_SUMMARY = ensure_path_sep(f'{ALLURE_DIR}widgets/summary.json')

#jenkins容器的项目目录
JENKIN_ALLURE = ensure_path_sep('/var/jenkins/workspace/auto/allure-results')


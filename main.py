import os

import pytest

from common.config import ROOT_DIR
from common.file_tools.from_excel_write_yaml import FromExcelWriteYaml
from common.file_tools.from_yaml_write_case import write_testcase

# 按间距中的绿色按钮以运行脚本。
if __name__ == "__main__":
    # 读取excel生成yaml用例
    FromExcelWriteYaml().write_yaml()

    # 通过yaml用例生成py测试用例
    write_testcase()

    # 执行用例
    args = [
        "-s",
        "-v",
        # "-n=2",  # 收集用例结果会出现重复执行的问题
        "--reruns=2",
        "--reruns-delay=3",
        f"{ROOT_DIR}test_case/xiaofa/RPA机器人自动拉群/test_automaticPullGroup_delete.py",
        # f"{ROOT_DIR}test_case/xiaofa/抽盲盒活动/test_lottery_time.py",
        # f"{ROOT_DIR}test_case/xiaofa/",
        f"--alluredir={ROOT_DIR}report/allure_results",
        "--clean-alluredir"
    ]
    pytest.main(args)
    # 生成allure报告
    cmd = f"allure generate {ROOT_DIR}report/allure_results -o {ROOT_DIR}report/allure_report -c {ROOT_DIR}report/allure_report"
    os.system(cmd)

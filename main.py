import os
import sys
import pytest
import subprocess as sp
sys.path.append(os.path.dirname(sys.path[0]))
from utils.allure.allure_report_data import AllureFileClean
from utils.file_tools.from_excel_write_yaml import FromExcelWriteYaml
from utils.file_tools.from_yaml_write_case import write_testcase
from utils.notification.ding_talk import DingTalkSendMsg
from utils.notification.email_control import SendReport
from utils.notification.wechat_send import WeChatSend
from utils import config
from utils.other.models import NotificationType
from common.config import ROOT_DIR,JENKINS_ALLURE



# 按间距中的绿色按钮以运行脚本。
if __name__ == "__main__":
    # 读取excel生成yaml用例
    FromExcelWriteYaml().write_yaml()

    #通过yaml用例生成py测试用例
    write_testcase()

    #执行用例
    try:
        args = [
            "-s",
            "-v",
            "-n=2",  # 收集用例结果会出现重复执行的问题
            "--reruns=1",
            "--reruns-delay=2",
            #f"{ROOT_DIR}/test_case/xiaofa/案源收藏/test_caseCollectAdd.py",
            f"{ROOT_DIR}/test_case/xiaofa/小法法工服务评价/",
            f"--alluredir={ROOT_DIR}/report/allure_results",
            #f"--alluredir={JENKINS_ALLURE}",
            "--clean-alluredir"
        ]
        pytest.main(args)

        # 生成allure报告 ，当jenkins集成由allure插件进行生成报告（所以这里要注释）
        cmd = f"allure generate {ROOT_DIR}/report/allure_results -o {ROOT_DIR}/report/allure_report -c {ROOT_DIR}/report/allure_report"
        sp.run(cmd, shell=True,capture_output=True,encoding='utf-8')
    except BaseException as e:
        raise e

    # 通知
    # allure_data = AllureFileClean().get_case_count()
    # notification_mapping = {
    #     # 钉钉通知
    #     NotificationType.DING_TALK.value: DingTalkSendMsg(allure_data).send_ding_notification,
    #     # 企微通知
    #     NotificationType.WECHAT.value: WeChatSend(allure_data).send_wechat_notification,
    #     # 邮件通知
    #     NotificationType.EMAIL.value: SendReport(allure_data).send
    #     # NotificationType.FEI_SHU.value: FeiShuTalkChatBot(allure_data).post
    # }
    #
    # if config.notification_type != NotificationType.DEFAULT.value:
    #     notify_type = config.notification_type.split(",")
    #     for i in notify_type:
    #         notification_mapping.get(i.strip())()

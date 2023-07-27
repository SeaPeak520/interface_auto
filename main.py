import os
import pytest

from common.allure.allure_report_data import AllureFileClean
from common.file_tools.from_excel_write_yaml import FromExcelWriteYaml
from common.file_tools.from_yaml_write_case import write_testcase
from common.notification.ding_talk import DingTalkSendMsg
from common.notification.email_control import SendReport
from common.notification.wechat_send import WeChatSend
from common.utils import config
from common.utils.models import NotificationType

# 按间距中的绿色按钮以运行脚本。
if __name__ == "__main__":
    # 读取excel生成yaml用例
    FromExcelWriteYaml().write_yaml()

    # 通过yaml用例生成py测试用例
    #write_testcase()

    # 执行用例
    # args = [
    #     "-s",
    #     "-v",
    #     # "-n=2",  # 收集用例结果会出现重复执行的问题
    #     "--reruns=2",
    #     "--reruns-delay=3",
    #     # "./test_case/xiaofa/RPA机器人自动拉群/test_automaticPullGroup_delete.py",
    #     "./test_case/xiaofa/律师曝光/",
    #     "--alluredir=./report/allure_results",
    #     "--clean-alluredir"
    # ]
    # pytest.main(args)
    # # 生成allure报告
    # cmd = "allure generate ./report/allure_results -o ./report/allure_report -c ./report/allure_report"
    # os.system(cmd)

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

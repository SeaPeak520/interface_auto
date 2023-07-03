import os
import smtplib
import sys
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
from typing import Dict

from common.log.log_control import LogHandler
from common.utils import config
from common.utils.models import EmailInfo

sys.path.append(os.path.dirname(sys.path[0]))


class EmailHelper:
    def __init__(self, email_info: Dict[str, str | int] = None) -> None:
        """
        :param email_info:
        email_info = {
        "host": "smtp.qq.com",
        "port": 465,
        "user": "1@qq.com",
        "pwd": '1'
    }
        """
        if not email_info:
            email_info = {
                "host": config.email['host'],
                "port": int(config.email['port']),
                "user": config.email['user'],
                "pwd": config.email['password'],
            }
        # 校验email_info格式并返回
        self.info = EmailInfo(**email_info)
        if self.info.port == 465:
            self.smtp = smtplib.SMTP_SSL(self.info.host, self.info.port)
            self.smtp.login(user=self.info.user, password=self.info.pwd)
        elif self.info.port == 25:
            self.smtp = smtplib.SMTP(self.info.host, self.info.port)
            self.smtp.login(user=self.info.user, password=self.info.pwd)
        else:
            self.log.error("输入正确的host和port")
        self.message = None
        self.log = LogHandler(os.path.basename(__file__))

    @staticmethod
    def _format_addr(sender: str) -> str:
        """
        :param sender: 测试<1@qq.com> 发件人
        :return: =?utf-8?b?5rWL6K+V?= <1@qq.com>
        """
        addr = parseaddr(sender)
        return formataddr(addr)

    # TODO Rename this here and in `message_text`, `message_html` and `message_attr`
    def _extracted_from_message_attr(self, message_content):
        """
        :param message_content: {
        "message_content": "Python自动发送的邮件",   邮件内容
        "message_subject": "您好，这是使用python登录QQ邮箱发送邮件的测试——zep",  定义邮件标题
        "from_user": '测试<1@qq.com>',   发件人的昵称
        "to_user": '测试组'   发件人的昵称
    }
        :return:
        """
        self.message['From'] = self._format_addr(message_content['from_user'])
        self.message['To'] = message_content['to_user']
        self.message['Subject'] = Header(message_content['message_subject'], 'utf-8')

    # 文本
    def message_text(self, message_content: Dict[str, str]) -> None:
        """
        :param message_content:
        message_content = {
             "message_content": "Python自动发送的邮件",    邮件内容
             "message_subject": "您好，这是使用python登录QQ邮箱发送邮件的测试——zep",  定义邮件标题
             "from_user": '测试<1@qq.com>',  发件人的昵称
             "to_user": '测试组',  发件人的昵称
         }
        :return:
        """
        self.message = MIMEText(message_content['message_content'], 'plain', 'utf-8')  # 邮件内容
        self._extracted_from_message_attr(message_content)

    def message_html(self, message_content: Dict[str, str]) -> None:
        """
        :param message_content:
        message_content = {
             "message_content": "Python自动发送的邮件",    邮件内容
             "message_subject": "您好，这是使用python登录QQ邮箱发送邮件的测试——zep",  定义邮件标题
             "from_user": '测试<1@qq.com>',  发件人的昵称
             "to_user": '测试组',  发件人的昵称
         }
        :return:
        """
        self.message = MIMEText(message_content['message_content'], 'html', 'utf-8')  # 邮件内容
        self._extracted_from_message_attr(message_content)

    def message_attr(self, message_content: Dict[str, str]) -> None:
        """
        :param message_content:
         message_content = {
         "message_content": "Python自动发送的邮件",   邮件内容
         "message_subject": "您好，这是使用python登录QQ邮箱发送邮件的测试——zep",  定义邮件标题
         "from_user": '测试<1@qq.com>',  发件人的昵称
         "to_user": '测试组',  收件人的昵称
         "file": "E:\\auto_test\\new_new\\abc.py"  附件(文件路径)
     }
        :return:
        """
        file = message_content['file']
        self.message = MIMEMultipart()  # 创建一个带附件的实例
        self._extracted_from_message_attr(message_content)
        self.message.attach(MIMEText(message_content['message_content'], 'plain', 'utf-8'))  # 邮件正文内容
        att1 = MIMEText(open(file, 'rb').read(), 'base64', 'utf-8')
        att1["Content-Type"] = 'application/octet-stream'
        # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
        att1["Content-Disposition"] = f'attachment; filename={file.split("/")[-1]}'
        self.message.attach(att1)

    def sendmail(self, send: dict[str, str] = None) -> None:
        """
        :param send:
        _send = {
        "sender": "测试<1@qq.com>",   发件人邮箱
        "receivers": ['2@qq.com']   收件人邮箱列表
    }
        :return:
        """
        if not send:
            send = {
                "sender": config.email['sender'],
                "receivers": config.email['receivers'],
            }
        if isinstance(send['receivers'], str):  # 转换成list
            send['receivers'] = send['receivers'].strip('[').strip(']').replace("'", '').replace('"',
                                                                                                 '')  # 去掉 [ ] ' "字符串
            send['receivers'] = send['receivers'].split(',')  # 转换成list
        try:
            self.smtp.sendmail(send['sender'], send['receivers'], self.message.as_string())
            self.log.info("邮件发送成功")
        except smtplib.SMTPException as e:
            self.log.error(f"Error: 无法发送邮件,报错信息如下：{e}")


if __name__ == '__main__':
    # 用法
    info = {
        "host": "smtp.qq.com",
        "port": 465,
        "user": "1@qq.com",
        "pwd": '1'
    }

    content = {
        "message_content": "Python自动发送的邮件",
        "message_subject": "您好，这是使用python登录QQ邮箱发送邮件的测试——zep",
        "from_user": '测试<1@qq.com>',
        "to_user": '测试组'
    }
    _send = {
        "sender": "测试<1@qq.com>",
        "receivers": ['2@qq.com']
    }

    e = EmailHelper(info)
    e.message_text(content)
    e.sendmail(_send)

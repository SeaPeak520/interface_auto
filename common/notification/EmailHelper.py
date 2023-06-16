import smtplib
import os
import sys
from common.log.LogHandler import LogHandler
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import parseaddr, formataddr
from common.utils import config
sys.path.append(os.path.dirname(sys.path[0]))

class EmailHelper:
    def __init__(self, info: dict[str, str | int] = None) -> None:
        """
        :param host: 邮件地址
        :param port: 邮件端口
        :param user: 要登录的用户
        :param password: 密码
        """
        if not info:
            info = {
                "host": config.email['host'],
                "port": int(config.email['port']),
                "user": config.email['user'],
                "pwd": config.email['password'],
            }
        self.log = LogHandler(os.path.basename(__file__))
        if info['port'] == 465:
            self.smtp = smtplib.SMTP_SSL(info['host'], info['port'])
            self.smtp.login(user=info['user'], password=info['pwd'])
        elif info['port'] == 25:
            self.smtp = smtplib.SMTP(info['host'], info['port'])
            self.smtp.login(user=info['user'], password=info['pwd'])
        else:
            self.log.error("输入正确的host和port")

    def _format_addr(self, s: str) -> str:
        """
        :param s: 测试<1@qq.com>
        :return: =?utf-8?b?5rWL6K+V?= <1@qq.com>
        """
        addr = parseaddr(s)
        return formataddr(addr)

    # TODO Rename this here and in `message_text`, `message_html` and `message_attr`
    def _extracted_from_message_attr_10(self, content):
        self.message['From'] = self._format_addr(content['from_user'])
        self.message['To'] = content['to_user']
        self.message['Subject'] = Header(content['message_subject'], 'utf-8')
        
    # 文本
    # content = {
    #         "message_content": "Python自动发送的邮件",
    #         "message_subject": "您好，这是使用python登录QQ邮箱发送邮件的测试——zep",
    #         "from_user": '测试<1@qq.com>',
    #         "to_user": '测试组',
    #     }
    def message_text(self, content: dict[str, str]) -> None:
        """
        :param message_subject: 定义邮件标题
        :param from_user: 发件人的昵称
        :param to_user: 收件人的昵称
        :param message_content: 邮件内容
        :return:
        """
        self.message = MIMEText(content['message_content'], 'plain', 'utf-8')  # 邮件内容
        self._extracted_from_message_attr_10(content)

    def message_html(self, content: dict[str, str]) -> None:
        """
        :param message_subject: 定义邮件标题
        :param from_user: 发件人的昵称
        :param to_user: 收件人的昵称
        :param message_content: 邮件内容
        :return:
        """
        self.message = MIMEText(content['message_content'], 'html', 'utf-8')  # 邮件内容
        self._extracted_from_message_attr_10(content)

    # content = {
    #     "message_content": "Python自动发送的邮件",
    #     "message_subject": "您好，这是使用python登录QQ邮箱发送邮件的测试——zep",
    #     "from_user": '测试<1@qq.com>',
    #     "to_user": '测试组',
    #     "file": "E:\\auto_test\\new_new\\abc.py"
    # }
    def message_attr(self, content: dict[str, str]) -> None:
        """
        :param message_subject: 定义邮件标题
        :param from_user: 发件人的昵称
        :param to_user: 收件人的昵称
        :param message_content: 邮件内容
        :param file: 附件(文件路径)
        :return:
        """
        file = content['file']
        self.message = MIMEMultipart()  # 创建一个带附件的实例
        self._extracted_from_message_attr_10(content)
        self.message.attach(MIMEText(content['message_content'], 'plain', 'utf-8'))  # 邮件正文内容
        att1 = MIMEText(open(file, 'rb').read(), 'base64', 'utf-8')
        att1["Content-Type"] = 'application/octet-stream'
        # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
        att1["Content-Disposition"] = f'attachment; filename={file.split("/")[-1]}'
        self.message.attach(att1)

    # sender = "测试<321013@qq.com>",receiver = ['4602@qq.com']
    def sendmail(self, send: dict[str, str] = None) -> None:
        """
        :param sender: 发件人邮箱
        :param receivers: 收件人邮箱列表
        :return:
        """
        if not send:
            send = {
                "sender": config.email['sender'],
                "receivers": config.email['receivers'],
            }
        if isinstance(send['receivers'], str):  # 转换成list
            send['receivers'] = send['receivers'].strip('[').strip(']').replace("'", '').replace('"','')  # 去掉 [ ] ' "字符串
            send['receivers'] = send['receivers'].split(',')  #转换成list
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
    send = {
        "sender": "测试<1@qq.com>",
        "receivers": ['2@qq.com']
    }

    e = EmailHelper(info)
    e.message_text(content)
    e.sendmail(send)

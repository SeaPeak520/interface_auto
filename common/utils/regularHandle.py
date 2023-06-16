import datetime
import os
import random
import re


class Context:
    """ 正则替换 """
    def __init__(self):
        from faker import Faker
        self.faker = Faker(locale='zh_CN')

    @classmethod
    def random_int(cls) -> int:
        """
        :return: 随机数
        """
        return random.randint(0, 5000)

    def get_phone(self) -> int:
        """
        :return: 随机生成手机号码
        """
        return self.faker.phone_number()

    def get_id_number(self) -> int:
        """

        :return: 随机生成身份证号码
        """

        return self.faker.ssn()

    def get_female_name(self) -> str:
        """

        :return: 女生姓名
        """
        return self.faker.name_female()

    def get_male_name(self) -> str:
        """

        :return: 男生姓名
        """
        return self.faker.name_male()

    def get_email(self) -> str:
        """

        :return: 生成邮箱
        """
        return self.faker.email()

    @classmethod
    def get_time(cls) -> str:
        """
        计算当前时间
        :return:
        """
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def today_date(cls):
        """获取今日0点整时间"""

        _today = datetime.date.today().strftime("%Y-%m-%d") + " 00:00:00"
        return str(_today)

    @classmethod
    def time_after_week(cls):
        """获取一周后12点整的时间"""

        return (datetime.date.today() + datetime.timedelta(days=+6)).strftime(
            "%Y-%m-%d"
        ) + " 00:00:00"



class config_regular:
    @classmethod
    def host(cls,num : int= 1) -> str:
        from common.utils import config
        """ 获取接口域名 """
        return config.info[f'host{num}']

def regular(target):
    """
    用于解析测试用例数据时
    使用正则替换请求数据
    :param target: 用例数据，str格式
    :param str类型或json类型 的用例数据
    :return:
    getattr(config_regular(), func_name)(value_name) 执行config_regular类的 func_name函数，传入value_name
    """
    from common.log.LogHandler import LogHandler
    log = LogHandler(os.path.basename(__file__))
    try:
        regular_pattern = r'\${{(.*?)}}'
        if key_list := re.findall(regular_pattern, target):   #正则匹配到的值集合['host(1)', 'host(2)']
            # value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']  #?
            # if any(i in key_list for i in value_types):  #key 在value_type中执行
            #     for key in key_list:
            #         func_name = key.split(":")[1].split("(")[0]
            #         value_name = key.split(":")[1].split("(")[1][:-1]
            #         if value_name == "":
            #             value_data = getattr(config_regular(), func_name)()
            #         else:
            #             value_data = getattr(config_regular(), func_name)(*value_name.split(","))
            #         regular_int_pattern = r'\'\${{(.*?)}}\''
            #         target = re.sub(regular_int_pattern, str(value_data), target)
            # else:
                #key : host(1)
            for key in key_list:
                func_name = key.split("(")[0]    #host
                value_name = key.split("(")[1][:-1]  #1
                if value_name == "":
                    #默认取第一个 1
                    value_data = getattr(config_regular(), func_name)()
                else:
                    value_data = getattr(config_regular(), func_name)(value_name)  #*value_name.split(",") == 1
                regular_int_pattern = r'\$\{\{func\(value\)\}\}'.replace('func',func_name).replace('value',value_name)
                target = re.sub(regular_int_pattern, str(value_data), target)  #把host替换成config文件的值
        return target

    except AttributeError:
        log.error(f"未找到对应的替换的数据, 请检查数据是否正确 {target}", )
        raise
    except IndexError:
        log.error("yaml中的 ${{}} 函数方法不正确，正确语法实例：${{get_time()}}")
        raise


if __name__ =='__main__':
    #from common.config import TESTDATA_DIR
    #from common.file_tools.get_yaml_data_analysis import CaseData
    #print('test')
    #file = f'{TESTDATA_DIR}test.yaml'
    # print(YamlHandler(file).get_yaml_data())
    print(Context().get_id_number())
    # print(file)


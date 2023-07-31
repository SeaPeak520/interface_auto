import ast
import datetime
import os
import random
import re

from common.utils.models import TestCase



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
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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

    @classmethod
    def host(cls, value) -> str:
        """ 获取接口域名 """
        from common.utils import config
        return eval(f"config.host.{value}")


def config_regular(target: str) -> str:
    """
    用于解析测试用例数据时
    使用正则替换请求数据
    ${{host}}
    :param target: 用例数据，str格式
    str类型或json类型 的用例数据
    :return:
    getattr(config_regular(), func_name)(value_name) 执行config_regular类的 func_name函数，传入value_name
    """
    from common.log.log_control import LogHandler
    log = LogHandler(os.path.basename(__file__))
    try:
        regular_pattern = r'\${{(.*?)}}'
        if key_list := re.findall(regular_pattern, target):  # 正则匹配到的值集合['gateway_host', 'callback_host']
            for key in key_list:
                func_name = '_'.join(key.split("_")[1:])  # host
                value_data = getattr(Context(), func_name)(key)  # 获取对应的域名https://gateway.com
                pattern = re.compile(r'\$\{\{func\}\}'.replace('func', key))
                target = re.sub(pattern, str(value_data), target)  # 把host替换成config文件的值
        return target

    except AttributeError:
        log.error(f"未找到对应的替换的数据, 请检查数据是否正确 {target}", )
        raise
    except IndexError:
        log.error("yaml中的 ${{}} 函数方法不正确，正确语法实例：${{get_time}}")
        raise


def cache_regular(target: str) -> str:
    """
    用于解析测试用例数据时
    使用正则替换缓存数据
    $cache{login_init}  $cache{int:login_init}
    :param target: 用例数据，str格式
    str类型或json类型 的用例数据
    :return:
    getattr(Context(), func_name)(value_name) 执行Context类的 func_name函数，传入value_name
    """
    from common.log.log_control import LogHandler
    from common.utils.cache_control import CacheHandler
    log = LogHandler(os.path.basename(__file__))
    try:
        # 正则获取 $cache{login_init}中的值 --> login_init
        regular_pattern = r"\$cache\{(.*?)\}"
        if key_list := re.findall(regular_pattern, target):  # 正则匹配到的值集合['login_init'] #int:login_init
            value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']
            for key in key_list:
                if any(i in key for i in value_types) is True:
                    value_type = key.split(":")[0]
                    regular_data = key.split(":")[1]
                    pattern = re.compile(r'\'\$cache\{' + value_type + ":" + regular_data + r'\}\'')
                    cache_data = eval(f"{value_type}({CacheHandler.get_cache(regular_data)})")
                else:
                    pattern = re.compile(r'\$cache\{' + key + r'\}')
                    cache_data = CacheHandler.get_cache(key)
                # 使用sub方法，替换已经拿到的内容
                target = re.sub(pattern, str(cache_data), target)
        return target
    except AttributeError:
        log.error(f"未找到对应的替换的数据, 请检查数据是否正确 {target}")
        raise
    except IndexError:
        log.error("yaml中的 ${{}} 函数方法不正确，正确语法实例：$cache{login_init}")
        raise

def teardown_regular(target: str) -> str:
    """
    用于解析测试用例数据时
    使用正则替换缓存数据
    $td{login_init}  $td{int:login_init}
    :param target: 用例数据，str格式
    str类型或json类型 的用例数据
    :return:
    getattr(Context(), func_name)(value_name) 执行Context类的 func_name函数，传入value_name
    """
    from common.log.log_control import LogHandler
    from common.utils.cache_control import CacheHandler
    log = LogHandler(os.path.basename(__file__))
    try:
        # 正则获取 $cache{login_init}中的值 --> login_init
        regular_pattern = r"\$td\{(.*?)\}"
        if key_list := re.findall(regular_pattern, target):  # 正则匹配到的值集合['login_init'] #int:login_init
            value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']
            for key in key_list:
                if any(i in key for i in value_types) is True:
                    value_type = key.split(":")[0]
                    regular_data = key.split(":")[1]
                    pattern = re.compile(r'\'\$td\{' + value_type + ":" + regular_data + r'\}\'')
                    cache_data = eval(f"{value_type}({CacheHandler.get_cache(regular_data)})")
                else:
                    pattern = re.compile(r'\$td\{' + key + r'\}')
                    cache_data = CacheHandler.get_cache(key)
                # 使用sub方法，替换已经拿到的内容
                target = re.sub(pattern, str(cache_data), target)
        return target
    except AttributeError:
        log.error(f"未找到对应的替换的数据, 请检查数据是否正确 {target}")
        raise
    except IndexError:
        log.error("yaml中的 ${{}} 函数方法不正确，正确语法实例：$td{login_init}")
        raise
def yaml_case_regular(yaml_case) -> "TestCase":
    """
    没有依赖，直接进行缓存替换
    :param yaml_case:
    :return:
    """
    _regular_data = cache_regular(f"{yaml_case.dict()}")
    _regular_data = ast.literal_eval(_regular_data)
    return TestCase(**_regular_data)


if __name__ == '__main__':
    from common.config import TESTDATA_DIR
    from common.utils.yaml_control import YamlHandler
    from common.utils.cache_control import CacheHandler

    file = f'{TESTDATA_DIR}xiaofa/案源收藏/caseCollectAdd.yaml'
    CacheHandler.update_cache(cache_name='token', value='[1,2]')
    yaml_data = str(YamlHandler(file).get_yaml_data())
    print(config_regular(yaml_data))
    # print(yaml_case_regular(yaml_data))
    a = ast.literal_eval(cache_regular(yaml_data))
    print(a)
    print(type(a))
    print(type(a['caseCollectAdd']['headers']['authorization']))

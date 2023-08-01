import os
import sys

import allure
import redis

from utils.log.log_control import LogHandler
from utils import config

sys.path.append(os.path.dirname(sys.path[0]))


class RedisHelper:
    def __init__(self, host: str = config.redis.host, port: int = config.redis.port,
                 pwd: str = config.redis.pwd, db: str = config.redis.db):
        self.__redis_pool = redis.ConnectionPool(host=host,
                                                 port=port,
                                                 password=pwd,
                                                 db=db,
                                                 decode_responses=True)
        self.__redis_conn = redis.Redis(connection_pool=self.__redis_pool)
        self.pipe = self.__redis_conn.pipeline(transaction=True)
        self.log = LogHandler(os.path.basename(__file__))

    # 获取多个key的值，传键：r.mget('manager:service:num','oms:orderId20220711')
    @allure.step('执行redis查询键值')
    def mget(self, *args: tuple) -> list[list]:
        """
        :param args: 收集参数组成Tuple对象
        :return: [['11300000', '4']]
        """

        if not args:
            self.log.info('查询的key为空')
        else:
            self.log.info(f'批量查询的key：{args}')
            self.pipe.mget(args)
            result = self.pipe.execute()
            self.log.info(f'批量查询的结果为：{result}')
            return result

    # 设置多个键值，传键值的字典：
    @allure.step('执行redis配置键值')
    def mset(self, key_value_dict: dict[str, str | float]) -> list[bool]:
        """
        :param key_value_dict: #置多个键值，传键值的字典
                            {
                                 'test:4': 'Zarten_4',
                                 'test:5': 'Zarten_5'
                            }
        :return: [True] (List)
        """

        if not key_value_dict:
            self.log.info('查询的key为空')
        else:
            key_list = []
            value_list = []
            for key, value in key_value_dict.items():
                key_list.append(key)
                value_list.append(value)
            self.log.info(f'设置的key：{key_list}')
            self.log.info(f'设置的value：{value_list}')
            self.pipe.mset(key_value_dict)
            result = self.pipe.execute()
            self.log.info(f'设置结果：{result}')
            return result

    # 给已有的键设置新值，并返回原有的值，传键值：r.getset('test:4','123')
    @allure.step('执行redis给已有的键设置新值，并返回原有的值')
    def getset(self, *args: tuple) -> list[str]:
        """
        :param args: 收集参数组成Tuple对象
        :return: ['Zarten_4'] (List)
        """

        if not args:
            self.log.info('设置的key_value为空')
        else:
            self.log.info(f'设置的key_value：{args}')
            self.pipe.getset(args[0], args[1])
            result = self.pipe.execute()
            self.log.info(f'原key:{args[0]}的值为：{result}')
            return result

    # 删除键值，传键：r.delete('test:4','test:5')
    @allure.step('执行redis删除键值')
    def delete(self, *args: tuple) -> list[bool]:
        """
        :param args: 收集参数组成Tuple对象
        :return: [1, 1] (List)
        """

        if not args:
            self.log.info('查询的key为空')
        elif len(args) == 1:
            self.log.info(f'删除的key：{args[0]}')
            self.pipe.delete(args[0])
            result = self.pipe.execute()
            self.log.info(f'删除的结果为：{result}')
            return result
        else:
            for key in args:
                self.pipe.delete(key)
            self.log.info(f'批量删除的key：{args}')
            result = self.pipe.execute()
            self.log.info(f'批量删除的结果为：{result}')
            return result


if __name__ == '__main__':
    # 用法
    r = RedisHelper()
    print(r.mget('manager:service:num', 'oms:orderId20220711'))

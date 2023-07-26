import os
import sys
from typing import List, Text, Union

import allure
import pymysql
from dbutils.pooled_db import PooledDB

from common.exceptions.exceptions import DataAcquisitionFailed, ValueTypeError
from common.log.log_control import LogHandler
from common.utils import config
from common.utils.models import load_module_functions

sys.path.append(os.path.dirname(sys.path[0]))


class MysqlDB:
    # 初始化
    def __init__(self):
        self.conn = self.get_mysql_conn(config.mysql.host,
                                        config.mysql.port,
                                        config.mysql.user,
                                        config.mysql.pwd,
                                        config.mysql.db)
        self.cur = self.conn.cursor()
        self.log = LogHandler(os.path.basename(__file__))

    # 释放资源
    def __del__(self):
        try:
            # 关闭游标
            self.cur.close()
            # 关闭连接
            self.conn.close()
        except AttributeError as error:
            self.log.error("数据库关闭失败，失败原因 %s", error)

    def get_mysql_conn(self, host: str, port: int, user: str, pwd: str, db: str):
        """
        :param host: 数据库主机
        :param port: 数据库端口
        :param user: 数据库用户
        :param pwd: 数据库密码
        :param db: 数据库名称
        :return:
        """
        try:
            return PooledDB(
                creator=pymysql,
                mincached=0,  # 最小空闲数
                maxcached=3,  # 最大空闲数
                maxshared=5,  # 池中共享连接的最大数量。默认为0，即每个连接都是专用的，不可共享(不常用，建议默认)
                maxconnections=5,  # 被允许的最大连接数。默认为0，无最大数量限制。(视情况而定)
                blocking=True,
                # 连接数达到最大时，新连接是否可阻塞。默认False，即达到最大连接数时，再取新连接将会报错。(建议True，达到最大连接数时，新连接阻塞，等待连接数减少再连接)
                maxusage=0,  # 连接的最大使用次数。默认0，即无使用次数限制。(建议默认)
                setsession=None,  # 可选的SQL命令列表，可用于准备会话。(例如设置时区)
                host=host,
                port=port,
                user=user,
                passwd=pwd,
                db=db,
                use_unicode=True,  # True显示str，False显示byte
                charset='utf8',
            ).connection()
        except BaseException as e:
            self.log.error(f"数据库连接错误{e}")
            raise

    @allure.step('执行查询sql')
    def select(self, sql: str, state: str = 'all') -> Union[tuple, int]:
        """
        :param sql: 要执行的sql
        :param state: all| one | num
        :return: Tuple ((1, '2'),) | ('1') ; int 1
        """
        try:
            self.log.info(f'执行sql语句：{sql}')
            if state == 'num':
                num = self.cur.execute(sql)
                self.conn.commit()
                self.log.info(f'查询结果：{num}')
                return num
            else:
                self.cur.execute(sql)
                self.conn.commit()
                result = self.cur.fetchall() if state == 'all' else self.cur.fetchone()
                self.log.info(f'查询结果：{result}')
                return result
        except AttributeError as error:
            self.log.error("数据库连接失败，失败原因 %s", error)
            raise

    @allure.step('执行新增sql')
    def insert(self, sql: str) -> int:
        """
        :param sql: 要执行的sql
        :return: 1 (int) 插入的数量
        """
        try:
            self.log.info(f'执行sql语句：{sql}')
            num = self.cur.execute(sql)
            self.conn.commit()
            self.log.info(f'sql语句新增成功：{num}')
            return num
        except AttributeError as error:
            self.log.error("数据库连接失败，失败原因 %s", error)
            # 如果事务异常，则回滚数据
            self.conn.rollback()
            raise

    @allure.step('执行删除sql')
    def delete(self, sql: str) -> int:
        """
        :param sql: 要执行的sql
        :return: 1 (int) 删除的数量
        """
        try:
            self.log.info(f'执行sql语句：{sql}')
            num = self.cur.execute(sql)
            self.conn.commit()
            self.log.info(f'sql语句删除成功：{num}')
            return num
        except AttributeError as error:
            self.log.error("数据库连接失败，失败原因 %s", error)
            # 如果事务异常，则回滚数据
            self.conn.rollback()
            raise

    @allure.step('执行更新sql')
    def update(self, sql: str) -> int:
        """
        :param sql: 要执行的sql
        :return: 1 (int) 更新的数量
        """
        try:
            self.log.info(f'执行sql语句：{sql}')
            num = self.cur.execute(sql)
            self.conn.commit()
            self.log.info(f'sql语句更新成功：{num}')
            return num
        except AttributeError as error:
            self.log.error("数据库连接失败，失败原因 %s", error)
            # 如果事务异常，则回滚数据
            self.conn.rollback()
            raise


class SqlHandler(MysqlDB):

    def execution_sql(self, sql: str, state: str = 'all'):
        """
          :param sql: 要执行的sql
          :param state: num 查询数量 all查询所有 one查询单条
        """
        _sql_type = ['update', 'delete', 'insert', 'select']
        sql_type = sql[:6].lower()
        if any(i in sql_type for i in _sql_type):
            if sql_type == 'select':
                return load_module_functions(MysqlDB)[sql_type](self, sql, state)
            else:
                return load_module_functions(MysqlDB)[sql_type](self, sql)
        else:
            raise DataAcquisitionFailed(f"sql类型不正确，应为{_sql_type}")

    # state值控制查询单条还是全部，不传查全部，传one查单条,传num 查数量
    def execution_by_sql_type(self, sql: Union[List, None, Text], state: str = 'all'):
        if isinstance(sql, list):
            return [self.execution_sql(i, state) for i in sql]
        elif isinstance(sql, str):
            return self.execution_sql(sql, state)
        else:
            raise ValueTypeError(f"传入数据类型不正确，接受的是list或str: {sql}")


if __name__ == "__main__":
    # 用法
    ss_sql = "select * from table where user_id=1 and case_id=1;"
    # sqkl = ["select * from "]
    s = SqlHandler()
    print(s.sql_handle(_sql, state='num'))

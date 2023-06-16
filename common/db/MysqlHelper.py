from typing import List, Text, Union
import allure
import pymysql
import sys
import os
from dbutils.pooled_db import PooledDB
from common.utils import config
from common.exceptions.exceptions import DataAcquisitionFailed, ValueTypeError
from common.log.LogHandler import LogHandler
from common.utils.models import load_module_functions
from common.assertion import assert_type

sys.path.append(os.path.dirname(sys.path[0]))

class MysqlHelper:
    # 初始化
    def __init__(self):
        self.conn = self.getmysqlconn(config.mysql['test_host'],
                                      int(config.mysql['test_port']),
                                      config.mysql['test_user'],
                                      config.mysql['test_pwd'],
                                      config.mysql['test_db'])
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

    def getmysqlconn(self, host: str, port: int, user: str, pwd: str, db: str):
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
    def select(self, sql: str, state: str = 'all') -> Union[tuple,int]:
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

#传单条sql
class SetUpTeardownMysql(MysqlHelper):

    def mapping_sqltype(self):
        return load_module_functions(MysqlHelper)
    def judge(self,sql: str,state: str='all'):
        """
          :param sql: 要执行的sql
          :param state: num 查询数量 all查询所有 one查询单条
        """
        _sqltype = ['update', 'delete', 'insert', 'select']
        sqltype = sql[:6].lower()
        if any(i in sqltype for i in _sqltype):
            if sqltype == 'select':
                return self.mapping_sqltype()[sqltype](self,sql,state)
            else:
                return self.mapping_sqltype()[sqltype](self,sql)
        else:
            raise DataAcquisitionFailed(f"sql类型不正确，应为{_sqltype}") 
    
    #_type值，传num
    #state值控制查询单条还是全部，不传查全部，传one查单条
    def setup_teardown_sql(self, sql: Union[List,None,Text],state: str='all'):
        if isinstance(sql, list):
            return [self.judge(i,state) for i in sql]
        elif isinstance(sql, str):
            return self.judge(sql,state)
        else:
            raise ValueTypeError(f"sql数据类型不正确，接受的是list或str:{sql}")
        
        
class AssertExecution(SetUpTeardownMysql):
    """ 处理断言sql数据 """
    def assert_execution(self, sql_data: Union[list,Text], sql_assert: Union[list,Text]):
        """
         执行 sql, 负责处理 yaml 文件中的断言需要执行多条 sql 的场景，最终会把所有数据校验后，以布尔类型返回
        :param sql_data: sql
        :param sql_assert: 校验数据（数量）
        :return:
        """
        try:
            if isinstance(sql_data,str):
                if not sql_data and not sql_assert:
                    return None
                if (sql_data and not sql_assert) or (not sql_data and sql_assert):
                    raise BaseException("校验语句和校验值不匹配，请检查")
                if sql_data:
                    _sql_type = ['update', 'delete', 'insert', 'select']
                    if all(i not in sql_data for i in _sql_type):
                        raise DataAcquisitionFailed("数据库校验的sql语句语法有问题")
                    num = self.setup_teardown_sql(sql_data,state='num')
                    assert_type.equals(num,int(sql_assert),'数据库校验不通过')
                    return True
            elif isinstance(sql_data, list):
                if not sql_data and not sql_assert:
                    return None        
                if len(sql_data) != len(sql_assert):
                    raise BaseException("校验语句和校验值不匹配，请检查")
                _sql_type = ['update', 'delete', 'insert', 'select']
                for k,sql in enumerate(sql_data):
                    if (sql and not sql_assert[k]) or (not sql and sql_assert[k]):
                        raise BaseException("校验语句和校验值不匹配，请检查")
                    if sql:
                        _sql_type = ['update', 'delete', 'insert', 'select']
                        if all(i not in sql for i in _sql_type):
                            raise DataAcquisitionFailed("数据库校验的sql语句语法有问题")
                        num = self.setup_teardown_sql(sql,state='num')
                        assert_type.equals(num,int(sql_assert[k]),'数据库校验不通过')
                        return True
            else:
                raise ValueTypeError("sql数据类型不正确，接受的是list或str")
        except Exception as error_data:
            self.log.error(f"数据库连接失败，失败原因: {error_data}")
            raise error_data   


if __name__ == "__main__":
    # 用法
    sql = "select * from table where id in (515,542);"
    sql_assert = '1'
    b = AssertExecution().assert_execution(sql,sql_assert)
    print(b)

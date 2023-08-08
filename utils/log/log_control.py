import logging
import os
import sys
import time

from common.config import ROOT_DIR
from utils.other.file_control import create_file
from common.config.setting import ensure_path_sep



# 格式化日志内容（新增变量file_name）
class AppFilter(logging.Filter):
    def __init__(self, file: str) -> None:
        """
        :param file: log_control.py （文件名称）
        """
        self.file = file

    def filter(self, record):
        record.file_name = self.file
        return True


class LogHandler:
    level_relations = {
        'notset': logging.NOTSET,
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    def __init__(self, file: str = os.path.basename(__file__), levels: str = 'info') -> None:
        """
        :param file: log_control.py （文件名称） 在哪个文件执行输出的日志
        """
        self.file = file

        # 创建日志记录器
        self.logger = logging.getLogger()
        # 设置日志记录器的默认等级
        # self.logger.setLevel(logging.NOTSET)
        self.logger.setLevel(self.level_relations.get(levels))

        # 获取当前日期
        self.date = time.strftime("%Y-%m-%d", time.localtime())
        # 获取项目目录
        self.path = ROOT_DIR

        # 指定输出的格式和内容
        self.__format = '[%(levelname)s - %(asctime)s - %(file_name)s]: %(message)s'
        # 指定时间格式
        self.__date = '%Y-%m-%d %H:%M:%S'

    # 建立通道
    def set_handler(self, levels: str) -> None:
        # 把文件变量添加到过滤器里，否则格式化日志时，file_name变量会报错
        self.logger.addFilter(AppFilter(self.file))
        if levels == 'error':
            self.err_file = ensure_path_sep(f'{self.path}/Log/err_{self.date}.log')
            # 不存在则创建日志文件
            create_file(self.err_file)
            # 创建文件处理器
            self.err_handler = logging.FileHandler(self.err_file, encoding='utf-8')
            # 自定义打印格式内容
            self.err_handler.setFormatter(logging.Formatter(self.__format, datefmt=self.__date))
            # 添加文件处理器
            self.logger.addHandler(self.err_handler)
        elif levels == 'warning':
            self.warning_file = ensure_path_sep(f'{self.path}/Log/warning_{self.date}.log')
            create_file(self.warning_file)
            self.warning_handler = logging.FileHandler(self.warning_file, encoding='utf-8')
            self.warning_handler.setFormatter(logging.Formatter(self.__format, datefmt=self.__date))
            self.logger.addHandler(self.warning_handler)
        else:
            self.info_file = ensure_path_sep(f'{self.path}/Log/info_{self.date}.log')
            create_file(self.info_file)
            self.handler = logging.FileHandler(self.info_file, encoding='utf-8')
            self.handler.setFormatter(logging.Formatter(self.__format, datefmt=self.__date))
            self.logger.addHandler(self.handler)

    def remove_handler(self, levels: str) -> None:
        if levels == 'error':
            self.logger.removeHandler(self.err_handler)
        elif levels == 'warning':
            self.logger.removeHandler(self.warning_handler)
        else:
            self.logger.removeHandler(self.handler)

    def debug(self, log_meg: str) -> None:
        self.set_handler('debug')
        self.logger.debug(log_meg)
        self.remove_handler('debug')

    def info(self, log_meg: str) -> None:
        self.set_handler('info')
        self.logger.info(log_meg)
        self.remove_handler('info')

    def warning(self, log_meg: str) -> None:
        self.set_handler('warning')
        self.logger.warning(log_meg)
        self.remove_handler('warning')

    def error(self, log_meg: str) -> None:
        self.set_handler('error')
        self.logger.error(log_meg)
        self.remove_handler('error')

    def critical(self, log_meg: str) -> None:
        self.set_handler('critical')
        self.logger.critical(log_meg)
        self.remove_handler('critical')


if __name__ == "__main__":
    # 用法
    m = LogHandler(os.path.basename(__file__))
    m.info("This is debug messageaaaaa")

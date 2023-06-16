import os
import sys
from typing import Text
sys.path.append(os.path.dirname(sys.path[0]))

# 创建目录
def mk_dir(path: str) -> None:
    """
    :param path: 目录路径
    :return:
    """
    # 去除首位空格
    path = path.strip()
    # 去除尾部"\\"
    path = path.rstrip("\\")
    # 去除尾部"/"
    path = path.rstrip("/")

    # 判断路径是否存在
    is_exists = os.path.exists(path)
    if not is_exists:
        try:
            os.makedirs(path)
        except Exception as e:
            print(e)


def ensure_path_sep(path: Text) -> Text:
    """兼容 windows 和 linux 不同环境的操作系统路径 """
    if "/" in path:
        path = os.sep.join(path.split("/"))

    if "\\" in path:
        path = os.sep.join(path.split("\\"))

    return path


if __name__ == '__main__':
    a = ensure_path_sep('E:/pythonProject\\new\common\\utils/ReadYaml.py')
    print(a)

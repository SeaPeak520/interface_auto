import jsonpath
import os
import sys

sys.path.append(os.path.dirname(sys.path[0]))

# 通过表达式获取对应的数据
def get_value(data: dict, key: str) -> list[str | int | float]:
    """
    :param data: 进行匹配的dict数据
    :param key: 表达式'$.code'：从根查找code键
    :return:
    """
    return jsonpath.jsonpath(data, key)

# 替换模板文件内容
def alter_file_content(datafile: str, source_str: str, replace_str: str) -> None:
    """
    :param datafile: 文件路径
    :param source_str: 匹配字段
    :param replace_str: 替换字段
    :param remark: CreateTestCase 初始化用例时用到
    :return:
    """
    # 获取dataFile文件的内容
    with open(datafile, 'r', encoding='utf-8') as fw:
        source = fw.readlines()

    # 读取每一行内容进行匹配，匹配到则替换对应的内容
    with open(datafile, 'w+', encoding='utf-8') as f:
        for line in source:
            if source_str in line:
                line = line.replace(source_str, replace_str)
            f.write(line)

# 目录下不存在文件则创建
def create_file(filename: str) -> None:
    """
    :param filename: 文件路径
    :return:
    """
    path = os.path.dirname(filename)
    if not os.path.isdir(path):
        os.makedirs(path)
    if not os.path.isfile(filename):
        fd = open(filename, mode='w', encoding='utf-8')
        fd.close()

# 查找文件所在的路径
def find_file(filename: str, search_path: str) -> list:
    """
    :param filename:  查找的文件名称
    :param search_path: 在哪个目录下查找
    :return:
    """
    return [
        os.path.join(root, filename)
        for root, dir, files in os.walk(search_path)
        if filename in files
    ]

if __name__ == '__main__':
    # 用法
    text = {
        "code": 500,
        "message": "拉群成功回调,查询数据不匹配",
        "data": 'null'
    }
    c_list = get_value(text, '$.code')
    print(c_list)
    print(c_list[0])

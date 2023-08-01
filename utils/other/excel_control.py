import os
import sys

import allure
import xlrd3

sys.path.append(os.path.dirname(sys.path[0]))


class ExcelHandler:
    def __init__(self, data_file: str):
        """
            :param book: book对象
        """
        self.book = xlrd3.open_workbook(data_file)

    # 获取sheet集合
    @property
    def get_sheet(self):
        return self.book.sheet_names()  # ['test', 'xiaofa']
    
    #获取某个sheet的标签数据
    def get_sheet_book_name(self, sheet_name):
        """
            return: sheet标签
        """
        return self.book.sheet_by_name(sheet_name)

    # 获取某个sheet的第一行数据（即标题）
    def get_title(self, sheet_data):
        """
            :param sheet_data: 某sheet页的数据
            :param sheet_data.row_values(1): 获取第一行的数据
        """
        return sheet_data.row_values(1)

    def _get_sheet_data(self, sheet_name):
        """
            :param sheet_data.nrows: 行数
            :param sheet_data.ncols: 列数
            :param sheet_data.cell_value(0,1)：第0行第1列的数据
        """
        sheet_book = self.get_sheet_book_name(sheet_name)
        sheet_data_list = []
        # 行循环(过滤掉标题)
        # sheet_data.nrows 行数
        for i in range(1, sheet_book.nrows):
            rowdata = {}
            # 列循环
            # sheet_data.ncols 列数
            for j in range(sheet_book.ncols):
                # key为第一行的数据(即标题)  
                key = sheet_book.cell_value(0, j)
                if isinstance(sheet_book.cell_value(i, j), float | int):
                    value = int(sheet_book.cell_value(i, j))
                else:
                    value = sheet_book.cell_value(i, j)
                rowdata[key] = value
            # 判断是否为空，为空则过滤
            if rowdata['用例名称'] and rowdata['用例标题'] and rowdata['请求地址']:
                sheet_data_list.append(rowdata)  # 把每一行数据添加到列表里

        return {sheet_name: sheet_data_list}

    def query_column_data(self, sheet_name: str, sheet_data, query_column_name, column_title):
        """
        :param sheet_name: sheet名称（打印日志）
        :param sheet_data: sheet页的所有数据
        :param query_column_name: 查找数据的条件（结合column_header使用），例column_title为'模块'，query_column_name为'小法管理'，
        即查找列为‘模块’的数据，再查找出包含‘小法管理’的数据
        :param column_title: 查找某列的标题头
        :return:
        """
        if any(query_column_name == data[column_title] for data in sheet_data):
            return [data for data in sheet_data if query_column_name == data[column_title]]
        else:
            raise BaseException(f'{query_column_name}在{sheet_name}中不存在，请检查')

    def get_all_sheet_data(self):
        return [self._get_sheet_data(sheet_name) for sheet_name in self.get_sheet]

    @allure.step('获取excel表数据')
    def get_sheet_data(self, sheet_name: str = None, case_name: str = None, module_name: str = None,
                       func_name: str = None) -> dict:
        """
        获取某sheet页的数据
            :param  sheet_name: sheet页名称，不传，直接返回所有的sheet数据
            :param  case_name: 用例名称6，查询列为'用例名称'，查询条件为case_name的数据
            :param  module_name: 模块名称4，查询列为'模块'，查询条件为module_name的数据
            :param  func_name: 功能名称5，查询列为'功能'，查询条件为func_name的数据
        """
        # 不传sheetName 则获取所有sheet的数据
        if not sheet_name:
            return self.get_all_sheet_data()

        # 判断sheetname是否在excel文件中
        if all(sheet_name not in i for i in self.get_sheet):
            raise BaseException(f'{sheet_name}和excel文件不匹配，请检查')

        # 获取sheet内所有的数据
        sheet_data = self._get_sheet_data(sheet_name)[sheet_name]

        ## caseName不为空，获取符合条件caseName（第六列）的“用例名称”数据
        if case_name:
            # 1、判断caseName是否在excel中
            return self.query_column_data(sheet_name, sheet_data, case_name, '用例名称')
        ## moduleName，获取符合条件moduleName（第4列）的模块数据
        if module_name:
            return self.query_column_data(sheet_name, sheet_data, module_name, '模块')

        ## funcName 获取符合条件funcName（第5列）的功能数据
        if func_name:
            return self.query_column_data(sheet_name, sheet_data, func_name, '功能')

        return sheet_data
        
if __name__ == '__main__':
    # 用法
    from common.config import TESTDATA_FILE

    b = ExcelHandler(TESTDATA_FILE)
    print(b.get_sheet_data())

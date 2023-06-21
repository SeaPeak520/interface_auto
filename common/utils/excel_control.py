import os
import sys

import allure
import xlrd3

sys.path.append(os.path.dirname(sys.path[0]))


class ExcelHandle:
    def __init__(self, dataFile: str):
        """
            :param book: book对象
        """
        self.book = xlrd3.open_workbook(dataFile)
    
    #获取sheet集合
    @property 
    def get_sheet(self):
        return self.book.sheet_names()  #['test', 'xiaofa']
    
    #获取某个sheet的标签数据
    def get_sheet_book_name(self,sheetName):
        """
            return: sheet标签
        """
        return self.book.sheet_by_name(sheetName) 
    
    #获取某个sheet的第一行数据（即标题）
    def get_title(self,sheet_data):
        """
            :param sheet_data.row_values(1): 获取第一行的数据
        """
        return sheet_data.row_values(1)
    
    def _get_sheet_data(self,sheetName):
        """
            :param sheet_data.nrows: 行数
            :param sheet_data.ncols: 列数
            :param sheet_data.cell_value(0,1)：第0行第1列的数据
        """
        sheet_book = self.get_sheet_book_name(sheetName)
        sheetdata_list = []
        # 行循环(过滤掉标题)
        #sheet_data.nrows 行数
        for i in range(1, sheet_book.nrows):
            rowdata = {}
            # 列循环
            #sheet_data.ncols 列数
            for j in range(sheet_book.ncols):
                # key为第一行的数据(即标题)  
                key = sheet_book.cell_value(0, j)  
                if isinstance(sheet_book.cell_value(i, j), float|int):
                    value = int(sheet_book.cell_value(i, j))
                else:
                    value = sheet_book.cell_value(i, j)
                rowdata[key] = value
            # 判断是否为空，为空则过滤
            if rowdata['用例名称'] and rowdata['用例标题'] and rowdata['请求地址']:  
                sheetdata_list.append(rowdata)  # 把每一行数据添加到列表里
    
        return {sheetName: sheetdata_list}
    
    def get_all_sheet_data(self):
        return [self._get_sheet_data(sheet_name) for sheet_name in self.get_sheet]

    @allure.step('获取excel表数据')
    def get_sheet_data(self,sheetName: str = None, caseName: str = None, moduleName: str = None,funcName: str = None) -> dict:
        """
            :param  sheetName: sheet页名称
            :param  caseName: 用例名称6
            :param  funcname: 功能名称5
            :param  moduleName: 模块名称4
        """
        #不传sheetName 则获取所有sheet的数据
        if not sheetName:
            return self.get_all_sheet_data()
        
        #判断sheetname是否在excel文件中
        if all(sheetName not in i for i in self.get_sheet):
             raise BaseException(f'{sheetName}和excel文件不匹配，请检查')

        #获取sheet内所有的数据
        sheet_data = self._get_sheet_data(sheetName)[sheetName]

        ## caseName不为空，获取符合条件caseName（第六列）的“用例名称”数据
        if caseName:
            #1、判断caseName是否在excel中
            if any(caseName == data['用例名称'] for data in sheet_data):
                return [data for data in sheet_data if caseName == data['用例名称']]
            
            else:
                raise BaseException(f'{caseName}在{sheetName}中不存在，请检查')

        ## moduleName，获取符合条件moduleName（第4列）的模块数据
        if moduleName:
            if any(moduleName == data['模块'] for data in sheet_data):
                return [data for data in sheet_data if moduleName == data['模块']]
            
            else:
                raise BaseException(f'{moduleName}在{sheetName}中不存在，请检查')

        ## funcName 获取符合条件funcName（第5列）的功能数据
        if funcName:
            if any(funcName == data['功能'] for data in sheet_data):
                return [data for data in sheet_data if funcName == data['功能']]
            
            else:
                raise BaseException(f'{funcName}在{sheetName}中不存在，请检查')
            
        return sheet_data
        
if __name__ == '__main__':
    # 用法
    from common.config import TESTDATA_FILE
    b = ExcelHandle(TESTDATA_FILE)
    print(b.get_sheet_data())

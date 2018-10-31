# -*- coding: utf-8 -*-
"""
Created on Thu Sep 27 10:40:46 2018

@author: lenovo
"""

import xlrd
import math
import numpy as np
import xlwt
import os

def read_excel(file):
    '''
    功能：读取Excel表格内容
    输入：File，Excel表格
    输出：字典
    '''
    ExcelFile=xlrd.open_workbook(file)
    sheet=ExcelFile.sheet_by_name('Sheet1')
    
    #获取整行或者整列的值
    dict_value = {}
    for i in range(4):
        cols=sheet.col_values(i+1)#第二列内容（度）
        key = cols[0]
        del cols[0]
        dict_value[key] = cols
    return dict_value


def average(List):
    return sum(List)/len(List)


def STDEVP(List):
    array_ = np.array(List)
    std = np.std(array_, ddof = 1)
    return std
    

def normal(List):
    max_min = max(List) - min(List)
    ave = average(List)
    normal = np.abs(np.array(List) - ave) / max_min 
    return normal


def weight(Dict):
    index = ['degree','closnesscentrality','betweenesscentrality','length']
    coff = []
    norms = []
    for i in index:
        norm = normal(Dict[i])
        ave = average(list(norm))
        std = STDEVP(list(norm))
        coeff_var = std / ave
        coff.append(coeff_var)
        norms.append(norm)
    w_List = np.around(np.array(coff)/sum(coff),3)
    return w_List,norms

def cal_information(url):
    dict_value = read_excel(url)
    w,norms = weight(dict_value)
    LOGS = []
    for norm in norms:
        LOG = []
        for x in norm:
            LOG_value = math.log2(x+1)
            LOG.append(LOG_value)
        LOGS.append(LOG)
    Info_sums =0
    for i in range(4):
        Info = np.array(LOGS[i]) *  w[i]
        Info_sum = sum(Info)
        Info_sums += Info_sum
    return Info_sums,w


if __name__ == "__main__":   
    if os.path.exists('./information/wuhan.xls'):
        os.remove('./information/wuhan.xls')
    workbook = xlwt.Workbook()
    table = workbook.add_sheet('Sheet1')
    table.write(0,0,'角度阈值')
    table.write(0,1,'信息量')
    table.write(0,2,'度权重')
    table.write(0,3,'邻近中心性权重')
    table.write(0,4,'中介中心性权重')
    table.write(0,5,'长度权重')
    for i in range(90):
        info,w = cal_information('info_param/wuhan'+str(i+1)+'_info_param.xls')
        table.write(i+1,0,i+1)
        table.write(i+1,1,info)
        table.write(i+1,2,w[0])
        table.write(i+1,3,w[1])
        table.write(i+1,4,w[2])
        table.write(i+1,5,w[3])
    workbook.save('./information/wuhan.xls')
    #dict_value = read_excel(r'Connection\wuhan90_degree.xls')
    #Info_sums,w = cal_information('info_param/wuhan90_info_param.xls')
    print('完成')
            
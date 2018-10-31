# -*- coding: utf-8 -*-
"""
Created on Thu Sep 27 10:40:46 2018

@author: lenovo
"""

import cal_networkx_eigenvalue as nxfeature
import cal_information as nxinfo
import time
import xlwt
import os


if __name__ == '__main__':
    start = time.time()
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
    file_num = 90
    shp_names,xls_names,info_param_names = nxfeature.create_file_name(file_num)
    for i in range(file_num):
        nodes,length = nxfeature.get_networkx_nodes(shp_names[i])
        edges = nxfeature.get_networkx_edges(xls_names[i])
        G = nxfeature.structure_graph_G(nodes,edges)
        print("{} 正在计算第{}个路网的特征值".format(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),i+1))
        feature_tab = nxfeature.cal_networkx_feature(G,length)
        print("{} 正在写入第{}个路网的特征值".format(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),i+1))
        nxfeature.write2excel(feature_tab,info_param_names[i])
        print("{} 正在计算第{}个路网的信息量".format(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),i+1))
        info,w = nxinfo.cal_information(info_param_names[i])
        print("{} 正在写入第{}个路网的信息量".format(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),i+1))
        table.write(i+1,0,i+1)
        table.write(i+1,1,info)
        table.write(i+1,2,w[0])
        table.write(i+1,3,w[1])
        table.write(i+1,4,w[2])
        table.write(i+1,5,w[3])
    workbook.save('./information/wuhan.xls')
    end = time.time()
    print("{} 写入excel完成,运行时间为{}s".format(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),end-start))
	
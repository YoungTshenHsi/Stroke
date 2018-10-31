# -*- coding: utf-8 -*-
"""
Created on Fri Oct 26 09:51:57 2018

@author: Administrator
"""

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import time
import math
import numpy as np
import xlrd
import sys

def read_from_txt(url):
    '''
    从txt读取数据
    :param: url: txt文件路径
    return: 读取的数据
    '''
    file = open(url)
    data = []
    for line in file.readlines():
        lineArr = line.strip().split('\n')
        data.append(float(lineArr[0]))
    file.close()
    return data
    

def read_from_excel(url):
    '''
    从excel文件读取数据
    :param url:excel文件路径
    return 读取的数据
    '''
    workbook = xlrd.open_workbook(url)
    table = workbook.sheet_by_index(0)
    x_data = []
    y_data = []
    nrows = table.nrows
    for i in range(1,nrows):
        row_val = table.row_values(i)
        x_data.append(row_val[0])
        y_data.append(row_val[1])
    return x_data,y_data


def distance_point2line(x,y,index):
    '''
    :param x: x轴的数据
    :param y: y轴的数据
    :param index: D-P算法中起点和终点在x和y中的索引
    return 点到线的距离列表
    '''
    dist = []
    start_p = [x[index[0]],y[index[0]]]
    end_p = [x[index[1]],y[index[1]]]
    based_v = [end_p[0]-start_p[0],end_p[1]-start_p[1]]
    for i in range(index[0]+1,index[1]):
        mid_p = [x[i],y[i]]
        edge_v = [mid_p[0]-start_p[0],mid_p[1]-start_p[1]]
        l_edge_v = math.sqrt(edge_v[0]**2+edge_v[1]**2)
        radian = cal_vec_angle(np.array(based_v),np.array(edge_v))
        d = l_edge_v * math.sin(radian)
        dist.append(d)
    return dist


def cal_vec_angle(v_1,v_2):
    """
    计算两条向量的夹角
    :param v_1:向量1
    :param v_2:向量2
    return 向量夹角
    """
    l_v_1 = np.sqrt(v_1.dot(v_1))
    l_v_2 = np.sqrt(v_2.dot(v_2))
    cos_t = v_1.dot(v_2)/(l_v_1 * l_v_2)
    t = np.arccos(cos_t)
    #angle = 180 * t/np.pi
    
    return t


def get_data_simplify(x,y,index):
    '''
    :param x: x轴的数据
    :param y: y轴的数据
    :param index: 索引列表
    return 简化后的数据
    '''
    x_simplify = []
    y_simplify = []
    for i in index:
        x_simplify.append(x[i])
        y_simplify.append(y[i])
        
    return x_simplify,y_simplify


def draw_picture(x,y,name,grad=[],pos=[]):
    '''
    :param x: x轴的数据
    :param y: y轴的数据
    :param name:保存图片的名称
    '''
    font_set = FontProperties(fname=r"c:\windows\fonts\simsun.ttc", size=12)
    plt.figure(figsize=(16, 10), dpi=96)
    axes = plt.subplot(111)
    axes.xaxis.grid(True, which='major')
    axes.yaxis.grid(True, which='major')
    plt.xticks(fontproperties='Times New Roman',fontsize=30)
    plt.yticks(fontproperties='Times New Roman',fontsize=30)
    plt.title('threshold-information',fontproperties='Times New Roman',fontsize = 30)
    plt.xlabel(u'Angle threshold',fontproperties='Times New Roman',fontsize = 40)
    plt.ylabel(u'Information',fontproperties='Times New Roman',fontsize = 40)
    axes.plot(x,y,'r',linewidth=2,linestyle="-")
    if len(grad) !=0:
        for i in range(len(grad)):
            plt.text(pos[i][0], pos[i][1], str(grad[i]), ha='center', va='bottom', fontproperties='Times New Roman',fontsize=20)
    plt.savefig(name+'.png',prop=font_set)
    #plt.show()


def get_data_simplify_index(x_data,y_data,index,threshold):
    '''
    :param x: x轴的数据
    :param y: y轴的数据
    :param index: 索引列表
    return 简化后数的索引
    '''
    forward_l = len(index)
    sign = True
    ncount = 1
    while sign:
        temp = []
        print("{} 第{}次综合,索引列表为{}".format(time.strftime('%Y-%m-%d %H:%M:%S',
          time.localtime(time.time())),ncount,index))
        for i in range(len(index)-1):
            a = [index[i],index[i+1]]
            if index[i]+1 == index[i+1]:
                for j in range(len(a)):
                    temp.append(a[j])
                continue
            dist = distance_point2line(x_data,y_data,a)
            if max(dist)>threshold:
                segmentation_p_index = dist.index(max(dist))
                a.insert(1,segmentation_p_index+1+index[i])
            for j in range(len(a)):
                temp.append(a[j])
        index = sorted(set(temp), key = temp.index)
        current_l = len(index)
        if current_l==forward_l:
            sign = False
        else:
            forward_l = current_l
        ncount += 1
    return index


def cal_gradient(x_data,y_data):
    '''
    :param x_data: x轴的数据
    :param y_data: y轴的数据
    return 斜率和标注斜率的位置
    '''
    gradient = []
    text_position = []
    for i in range(len(x_data)-1):
        k = (y_data[i+1] - y_data[i])/(x_data[i+1] - x_data[i])
        text_position.append([(x_data[i+1] + x_data[i])/2,(y_data[i+1] + y_data[i])/2])
        gradient.append(round(k,2))
    return gradient,text_position


def get_index_from_list(x,value):
    '''
    :param x:查找列表
    :param value:查找的值
    return value在x值中的索引
    '''
    index_l = []
    for i in range(len(x)):
        if x[i]==value:
            index_l.append(i)
        else:
            continue
    return index_l


def get_threshold_scope(x_data,min_val):
    '''
    :param x_data:查找列表
    :param min_val:查找索引
    return 阈值的范围
    '''
    threshold_scope = []
    for i in range(len(min_val)):
        temp_index = [min_val[i],min_val[i]+1]
        temp_scope = [x_data[temp_index[0]],x_data[temp_index[1]]]
        threshold_scope.append(temp_scope)
    return threshold_scope


if __name__ == '__main__':
    start = time.time()
    threshold = 0
    if(len(sys.argv)==1):
        threshold = 0.4
        print("{} 综合默认阈值为{}".format(time.strftime('%Y-%m-%d %H:%M:%S',
          time.localtime(time.time())),threshold))
    else:
        threshold = float(sys.argv[1])
        print("{} 综合使用阈值为{}".format(time.strftime('%Y-%m-%d %H:%M:%S',
          time.localtime(time.time())),threshold))
    url = 'test.xlsx'
    x_data,y_data = read_from_excel(url)
    index = [0,len(x_data)-1]
    index = get_data_simplify_index(x_data,y_data,index,threshold)
    x,y = get_data_simplify(x_data,y_data,index)
    gradient,position = cal_gradient(x,y)
    variance_ratio = list(map(abs,gradient))
    min_var_ratio = min(variance_ratio)
    min_val_index = get_index_from_list(variance_ratio,min_var_ratio)
    threshold_scope = get_threshold_scope(index,min_val_index)
    for i in range(len(threshold_scope)):
        print("{} 运行完成,最适角度范围为{}-{}".format(time.strftime('%Y-%m-%d %H:%M:%S',
          time.localtime(time.time())),threshold_scope[i][0],threshold_scope[i][1]))
    draw_picture(x_data,y_data,'before-'+str(threshold))
    draw_picture(x,y,'after-'+str(threshold),gradient,position)
    end = time.time()
    print("{} 运行完成,运行时间为{}s".format(time.strftime('%Y-%m-%d %H:%M:%S',
          time.localtime(time.time())),end-start))
    
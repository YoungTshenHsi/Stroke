# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 10:27:44 2018

@author: wo
"""

import networkx as nx
import xlrd
from osgeo import ogr
import os
import xlwt
import time

def get_networkx_edges(file_path):
    '''
    从excel表中获取复杂网络的连接关系edges
    '''
    workbook = xlrd.open_workbook(file_path)
    table = workbook.sheet_by_index(0)
    edges = []
    nrows = table.nrows
    for i in range(1,nrows):
        row_val = table.row_values(i)
        edges.append(tuple(row_val))
    return edges


def get_networkx_nodes(file_path):
    '''
    从shp文件中获取复杂网络的节点nodes
    '''
    nodes = []
    length = {}
    ds = ogr.Open(file_path,1)
    lyr = ds.GetLayer(0)
    for i in range(lyr.GetFeatureCount()):
        feat = lyr.GetFeature(i)
        Id = feat.GetField(0)
        temp_length = feat.GetField(1)
        length[Id] = temp_length
        nodes.append(Id)
    ds.Destroy()
    return nodes,length


def structure_graph_G(nodes,edges):
    G=nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    return G


def cal_networkx_feature(G,length):
    feature_tab = {}
    degree = nx.degree(G)
    closeness =nx.closeness_centrality(G)
    betweeness = nx.betweenness_centrality(G)
    keys = G.nodes()
    for key in keys:
        d_val = degree[key]
        c_val = closeness[key]
        b_val = betweeness[key] * (len(keys)-1) * (len(keys)-2)/2
        length_val = length[key]
        feature_tab[key] = [d_val,c_val,b_val,length_val]
    return feature_tab


def write2excel(net_feat_val,excel_name):
    '''
    功能：将数据写入excel
    输入：要写入的数据(字典), 生成excel的文件名
    '''
    if os.path.exists(excel_name):
        os.remove(excel_name)
    workbook = xlwt.Workbook()
    table = workbook.add_sheet('Sheet1')
    table.write(0,0,'Id')
    table.write(0,1,'degree')
    table.write(0,2,'closnesscentrality')
    table.write(0,3,'betweenesscentrality')
    table.write(0,4,'length')
    keys = list(net_feat_val.keys())
    for i in range(len(keys)):
        key = keys[i]
        values = net_feat_val[key]
        table.write(i+1,0,key)
        for j in range(len(values)):
            table.write(i+1,j+1,values[j])
    workbook.save(excel_name)
    
    
def create_file_name(file_num):
    shp_names = []
    xls_names = []
    info_param_names = []
    for i in range(file_num):
        shp_name = './wuhan'+str(i+1)+'/wuhan_'+str(i+1)+'.shp'
        xls_name = './Connection/wuhan_'+str(i+1)+'.xls'
        info_param_name = './info_param/wuhan'+str(i+1)+'_info_param.xls'
        shp_names.append(shp_name)
        xls_names.append(xls_name)
        info_param_names.append(info_param_name)
    return shp_names,xls_names,info_param_names
    
    
if __name__ == '__main__':
    start = time.time()
    file_num = 90
    shp_names,xls_names,info_param_names = create_file_name(file_num)
    for i in range(file_num-1,file_num):
        nodes,length = get_networkx_nodes(shp_names[i])
        edges = get_networkx_edges(xls_names[i])
        G = structure_graph_G(nodes,edges)
        print("{} 正在计算第{}个路网的特征值".format(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),i+1))
        feature_tab = cal_networkx_feature(G,length)
        print("{} 正在写入第{}个路网的特征值".format(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),i+1))
        write2excel(feature_tab,info_param_names[i])
    end = time.time()
    print("{} 写入excel完成,运行时间为{}s".format(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),end-start))
	
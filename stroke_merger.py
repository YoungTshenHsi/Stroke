# -*- coding: utf-8 -*-
"""
功能：根据给定角度合并路段生成路划

Created on Sun Sep 23 19:51:52 2018

@author: YoungTshenHsi
"""

from osgeo import ogr
import time
import os
import gdal
import numpy as np


def get_intersection_point(geom_1, geom_2):
    """
    获取两条道路的交点
    :param geom_1: 第一条道路的geometry
    :param geom_2: 第二条道路的geometry
    :return: 道路交点，以元组形式储存
    """
    
    return geom_1.Intersection(geom_2).GetPoints()[0]


def _get_object_index_in_list(anchor_list, target):
    """
    获取指定目标在指定list中的索引值
    :param anchor_list: 列表
    :param target: 对象，元组形式
    :return: 索引值
    """
    index = []
    for i in range(len(anchor_list)):
        if anchor_list[i] == target:
            index.append(i)
    if len(index) == 0:
        index.append(-1)

    return index

   
def judge_intersection_type(geom_1, geom_2):
    """
    判断两条道路相交的类型：(1)首尾相连；(2)道路交叉且交点在道路的geometry中；(3)道路交叉但交点不在道路的geometry中
    :param geom_1: 第一条道路的geometry
    :param geom_2: 第二天道路的geometry
    :return: 相交类型，用1,2,3表示
    """
    # 读取每条道路的点并存储为list，list里每一个对象为tuple
    path_1_p = ogr.Geometry.GetPoints(geom_1)
    path_2_p = ogr.Geometry.GetPoints(geom_2)
    
    end2end_sign = [1, len(path_1_p), len(path_2_p), len(path_1_p) * len(path_2_p)]

    intersect_p = get_intersection_point(geom_1, geom_2)

    index_1 = _get_object_index_in_list(path_1_p, intersect_p)
    index_2 = _get_object_index_in_list(path_2_p, intersect_p)

    if (index_1[0] + 1) * (index_2[0] + 1) == 0:
        sign = 3
    elif (index_1[0]+1) * (index_2[0]+1) in end2end_sign:
        sign = 1
    else:
        sign = 2

    return sign
    

def get_connectivity(lyr):
    """
    计算路网的连通关系
    :param lyr: 路网图层
    :return: 道路及其连接道路的FID，以字典的形式存在
    """
    con_rel = {}
    for i in range(lyr.GetFeatureCount()):
        print("{} 正在计算第{}条道路的连通关系".format(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())),i+1))
        feat_1 = lyr.GetFeature(i)
        geom_1 = feat_1.geometry()
        sub_con = []
        for j in range(i+1,lyr.GetFeatureCount()):
            feat_2 = lyr.GetFeature(j)
            geom_2 = feat_2.geometry()
            if geom_1.Intersects(geom_2):
                sub_con.append(j)
            del feat_2,geom_2
        del feat_1,geom_1
        con_rel[i] = sub_con
    return con_rel   


def cal_angle(geom_1,geom_2):
    """
    计算两条首尾相连道路的夹角
    :param geom_1:道路1的geometry对象
    :param geom_2:道路2的geometry对象
    return:道路夹角
    """
    path_1_p = ogr.Geometry.GetPoints(geom_1)
    path_2_p = ogr.Geometry.GetPoints(geom_2)
    intersect_p = get_intersection_point(geom_1, geom_2)
    index_1 = _get_object_index_in_list(path_1_p, intersect_p)
    index_2 = _get_object_index_in_list(path_2_p, intersect_p)
    
    if index_1[0]>0:
        v_1 = np.array([intersect_p[0] - path_1_p[index_1[0]-1][0],intersect_p[1] - path_1_p[index_1[0]-1][1]])
        if index_2[0]>0:
            v_2 = np.array([intersect_p[0] - path_2_p[index_2[0]-1][0],intersect_p[1] - path_2_p[index_2[0]-1][1]])
        else:
            v_2 = np.array([intersect_p[0] - path_2_p[index_2[0]+1][0],intersect_p[1] - path_2_p[index_2[0]+1][1]])
        angle = cal_vec_angle(v_1,v_2)
    else:
        v_1 = np.array([intersect_p[0] - path_1_p[index_1[0]+1][0],intersect_p[1] - path_1_p[index_1[0]+1][1]])
        if index_2[0]>0:
            v_2 = np.array([intersect_p[0] - path_2_p[index_2[0]-1][0],intersect_p[1] - path_2_p[index_2[0]-1][1]])
        else:
            v_2 = np.array([intersect_p[0] - path_2_p[index_2[0]+1][0],intersect_p[1] - path_2_p[index_2[0]+1][1]])
        angle = cal_vec_angle(v_1,v_2)
    return angle


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
    angle = 180 * t/np.pi
    
    return angle


def get_point_string(a):
    """
    根据道路两两相连的关系计算出相连道路的点串
    :param a: 两两相连列表
    return: 点串列表
    """
    b = []
    for j in range(len(a)-1):
        if len(a[j]) == 0:
            continue
        x = a[j]
        sign = True
        while sign:
            for i in range(j+1,len(a)):
                if x[-1] in a[i]:
                    a[i].remove(x[-1])
                    x=x+a[i]
                    a[i].pop()
                    break
                if x[0] in a[i]:
                    a[i].remove(x[0])
                    x = a[i] + x
                    a[i].pop()
                    break
                if i==len(a)-1:
                    sign = False
        b.append(x)
    return b


def create_shape_file(file_url, shp_name, spatial_ref, shp_type, field_list):
    """
    产生ShpFile格式的文件
    :param file_url:ShapeFile存放地址
    :param shp_name:shp文件名称
    :param spatial_ref:shp文件空间坐标系
    :param shp_type:shp类型
    :param field_list:字段列表，field_list[i][0]字段名称，field_list[i][1]字段类型，field_list[i][2]字段宽度
    :return:数据源、数据层、要素类
    """
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "Yes")
    ogr.RegisterAll()
    driver = ogr.GetDriverByName("ESRI ShapeFile")
    target_data_source = driver.CreateDataSource(file_url)
    target_lyr = target_data_source.CreateLayer(shp_name, spatial_ref, shp_type)
    for field in field_list:
        field_defined = ogr.FieldDefn(field[0], field[1])
        field_defined.SetWidth(field[2])
        field_defined.SetPrecision(4)
        target_lyr.CreateField(field_defined)
    feature_defined = target_lyr.GetLayerDefn()
    feature = ogr.Feature(feature_defined)

    return target_data_source, target_lyr, feature
    

def geom_union(pnt_str,lyr,fieldID):
    """
    合并点串表示的路段
    :param pnt_str:点串列表
    :param lyr:图层
    :param fieldID:合并时需要用到的字段ID
    :return 合并后的geometry对象,合并后对象的长度，合并后对象的ID
    """
    feat_1 = lyr.GetFeature(pnt_str[0])
    geom_1 = feat_1.geometry()
    ID = feat_1.GetField(fieldID[0])
    ID = str(ID)
    length = feat_1.GetField(fieldID[1])
    geom = ogr.Geometry.Clone(geom_1)
    for i in range(1,len(pnt_str)):
        feat_2 = lyr.GetFeature(pnt_str[i])
        geom_2 = feat_2.geometry()
        ID_2 = feat_2.GetField(fieldID[0])
        ID_2 = str(ID_2)
        length_2 = feat_2.GetField(fieldID[1])
        geom = geom.Union(geom_2)
        length = length + length_2
        ID = ID + '-' + ID_2
    return geom,length,ID


def get_con_fid(lyr,con_rel,threshold):
    """
    根据给定的阈值或相连道路的fid
    :param lyr: 图层
    :param con_rel: 连通关系列表
    :param threshold: 给定的阈值
    :return 点串列表,生成shp时要排除的道路fid列表
    """
    con_set = []
    del_fid = []
    for fid_1 in con_rel:
        if len(con_rel[fid_1]) == 0:
            continue
        feat_1 = lyr.GetFeature(fid_1)
        geom_1 = feat_1.geometry()
        for fid_2 in con_rel[fid_1]:
            feat_2 = lyr.GetFeature(fid_2)
            geom_2 = feat_2.geometry()
            if geom_1.Intersection(geom_2).GetGeometryType() != 1:
                continue
            if not geom_1.Intersection(geom_2).GetPoints() is None:
                con_sign = judge_intersection_type(geom_1, geom_2)
                if con_sign == 1:
                    angle = cal_angle(geom_1,geom_2)
                    if 180 - angle < threshold:
                        con_set.append([fid_1,fid_2])
    pnt_str = get_point_string(con_set)
    for i in range(len(pnt_str)):
        del_fid += pnt_str[i]
    
    return pnt_str,del_fid


def mkdir(path):
    """
    在当前文件夹生成指定文件夹
    :param path: 文件夹名称
    """
    folder = os.path.exists(path)
    if not folder:
        os.makedirs(path)            
    else:
        print ("{}存在".format(path))


def create_threshold_angle(nums):
    """
    生成阈值列表
    :param nums:阈值个数
    :return 阈值列表
    """
    thresholds = []
    step = int(90/nums)
    for i in range(nums):
        threshold = (i+1) * step
        thresholds.append(threshold)
    return thresholds

    
if __name__ == "__main__":
    start = time.time()
    url = r'./shapefile/WuhanRoad.shp'
    ds = ogr.Open(url,1)
    lyr = ds.GetLayer(0)
    lyrCount = lyr.GetFeatureCount()  #图层要素总数
    field_l = [['ID', ogr.OFTString, 20], ['Length', ogr.OFTReal, 16]]
    fieldID = [0,2]
    nums = 3  #等分3份为例
    con_rel = get_connectivity(lyr)
    thresholds = create_threshold_angle(nums)
    print('开始合并路划')
    for threshold in thresholds:
        print('角度阈值为{}时'.format(threshold))
        folderName = 'wuhan'+str(threshold)
        shp_name = 'wuhan_'+str(threshold)
        mkdir(folderName)
        if os.path.exists(folderName+'/'+shp_name+'.shp'):
            os.remove(folderName+'/'+shp_name+'.shp')
            os.remove(folderName+'/'+shp_name+'.dbf')
            os.remove(folderName+'/'+shp_name+'.prj')
            os.remove(folderName+'/'+shp_name+'.shx')
        tg_ds,tg_lyr,tg_feat = create_shape_file(folderName,shp_name,lyr.GetSpatialRef(),ogr.wkbMultiLineString,field_l)
        pnt_str,del_fid = get_con_fid(lyr,con_rel,threshold)
        count = 0
        for p in pnt_str:
            count = count + len(p)
            geom,length,ID = geom_union(p,lyr,fieldID)
            tg_feat.SetGeometry(geom)
            tg_feat.SetField("ID", ID)
            tg_feat.SetField("Length", length)
            tg_lyr.CreateFeature(tg_feat)
        for i in range(lyr.GetFeatureCount()):
            if i in del_fid:
                continue
            feat = lyr.GetFeature(i)
            length_1 = feat.GetField(fieldID[1])
            ID_1 = feat.GetField(fieldID[0])
            geom = feat.geometry()
            tg_feat.SetField("ID", str(ID_1))
            tg_feat.SetField("Length", length_1)
            tg_feat.SetGeometry(geom)
            tg_lyr.CreateFeature(tg_feat)
        tg_ds.Destroy()
        print("{} {}度合并后道路条数为{}条".format(time.strftime('%Y-%m-%d %H:%M:%S',
          time.localtime(time.time())),threshold,lyrCount-count+len(pnt_str)))
    ds.Destroy()
    end = time.time()
    print("{} 运行完成,运行时间为{}s".format(time.strftime('%Y-%m-%d %H:%M:%S',
          time.localtime(time.time())),end-start))

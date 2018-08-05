# -*- coding: utf-8 -*-
"""
功能：将两条相交但交点不在道路的地理对象中的交点添加到道路地理对象中
python版本：python 3.6
编译器：pycharm2018.2
@author:YoungTsHenHsi
时间：2018.8.4.10:40
"""

from osgeo import ogr
import os
import gdal


def get_road_geometry_by_id(data_source, road_id):
    """
    通过道路ID获取道路的Geometry
    :param data_source: ShapeFile文件数据源
    :param road_id: 道路的ID
    :return: 道路的Geometry
    """
    lyr = data_source.GetLayer(0)
    feat = lyr.GetFeature(road_id)
    geom = feat.geometry()
    return geom


def _geom2list(geom):
    """
    地理对象坐标转为list
    :param geom: 地理对象坐标
    :return: 坐标列表
    """
    return ogr.Geometry.GetPoints(geom)


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

    intersect_p = get_intersection_point(geom_1, geom_2)

    index_1 = _get_object_index_in_list(path_1_p, intersect_p)
    index_2 = _get_object_index_in_list(path_2_p, intersect_p)

    if (index_1[0] + 1) * (index_2[0] + 1) == 0:
        sign = 3
    elif index_1[0] * index_2[0] == 0 or index_1[0] * index_2[0] == (len(path_1_p) - 1) * (len(path_2_p) - 1):
        sign = 1
    else:
        sign = 2

    return sign


def intersection_point_insert(geom, insert_p):
    """
    当sign=3时，将交点插入到道路的geometry对象中
    :param geom: 地理目标对象
    :param insert_p: 插入点
    :return: 加入插入点后的list
    """
    anchor_list = _geom2list(geom)
    for i in range(len(anchor_list)-1):
        if (insert_p[0] - anchor_list[i][0]) * (insert_p[0] - anchor_list[i + 1][0]) <= 0\
                and (insert_p[1] - anchor_list[i][1]) * (insert_p[1] - anchor_list[i + 1][1]) <= 0:
            anchor_list.insert(i+1, insert_p)
            break
        else:
            continue

    return anchor_list


def list2wkb(anchor_list, geom_type):
    """
    将list转为wkb格式
    :param anchor_list: 列表
    :param geom_type: wkb类型
    :return: wkb格式数据
    """
    geom = ogr.Geometry(geom_type)
    for anchor in anchor_list:
        geom.AddPoint_2D(anchor[0], anchor[1])

    return geom


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


if __name__ == "__main__":
    url = r'E:/RoadData/Top300.shp'
    DataSource = ogr.Open(url, 1)
    layer = DataSource.GetLayer(0)
    f_url = "E:/RoadData/"
    shp = "NTop300"
    ref = layer.GetSpatialRef()
    shp_tp = ogr.wkbLineString
    field_l = [['ID', ogr.OFTInteger, 8], ['Length', ogr.OFTReal, 16]]
    if os.path.exists(f_url + shp + '.shp'):
        os.remove(f_url + shp + '.shp')
        os.remove(f_url + shp + '.dbf')
        os.remove(f_url + shp + '.prj')
        os.remove(f_url + shp + '.shx')

    DS, tar_lyr, tar_feature = create_shape_file(f_url, shp, ref, shp_tp, field_l)
    for k in range(layer.GetFeatureCount()):
        print("正在处理第{}个要素".format(k))
        feat1 = layer.GetFeature(k)
        road = feat1.GetField(0)
        length = feat1.GetField(2)
        print(length)
        geom1 = feat1.geometry()
        temp = ogr.Geometry.Clone(geom1)
        for j in range(layer.GetFeatureCount()):
            if k == j or (k == 246 and j == 279) or (k == 279 and j == 246):
                continue
            else:
                feat2 = layer.GetFeature(j)
                geom2 = feat2.geometry()
                # print("第{}比较,{}".format(j, geom1.Intersects(geom2)))
                if temp.Intersects(geom2):
                    mark = judge_intersection_type(geom1, geom2)
                    if mark == 3:
                        inter_p = get_intersection_point(geom1, geom2)
                        e_path_1_p = intersection_point_insert(geom1, inter_p)
                        new_geom = list2wkb(e_path_1_p, ogr.wkbLineString)
                        temp = new_geom
                    else:
                        continue
                else:
                    continue
        tar_feature.SetGeometry(ogr.CreateGeometryFromWkt(str(temp)))
        tar_feature.SetField("ID", road)
        tar_feature.SetField("Length", length)
        tar_lyr.CreateFeature(tar_feature)
    DS.Destroy()

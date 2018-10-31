# -*- coding: utf-8 -*-
"""
Created on Mon Oct 29 09:49:21 2018

@author: wo
"""

from osgeo import ogr
import operator
from shapely.geometry import LineString

url = r'./shapefile/multi-linestring.shp'
ds = ogr.Open(url,1)
lyr = ds.GetLayer(0)
feat = lyr.GetFeature(0)
geom = feat.geometry()
line = list(geom)[0].GetPoints()
for i in range(1,len(list(geom))):
    line_s_e = [(round(line[0][0],5),round(line[0][1],5)),(round(line[-1][0],5),round(line[-1][1],5))]
    temp = list(geom)[i].GetPoints()
    print(len(line),len(temp))
    temp_s_e = [(round(temp[0][0],5),round(temp[0][1],5)),(round(temp[-1][0],5),round(temp[-1][1],5))]
    connect_type = [operator.eq(line_s_e[0],temp_s_e[0]),operator.eq(line_s_e[0],temp_s_e[1]),operator.eq(line_s_e[1],temp_s_e[0]),operator.eq(line_s_e[1],temp_s_e[1])]
    sign = connect_type.index(True)
    if sign == 0:
        rev_temp = list(reversed(temp))
        rev_temp.pop()
        line = rev_temp + line
    if sign == 1:
        temp.pop()
        line = temp + line
    if sign == 2:
        line.pop()
        line = line + temp
    if sign == 3:
        temp.pop()
        rev_temp = list(reversed(temp))
        line = line + rev_temp
linestring = LineString(line)
print(linestring)
#print(list(geom)[1].GetPoints())
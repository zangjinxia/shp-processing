'''
@brief 实现线矢量的统计，并将长度写入矢量文件的属性中
@created 2020-12-3
@author zangjinxia
'''


from osgeo import ogr, osr
import numpy as np
import sys
import os
import math
import distutils.log

def geopoint_advanced(shpfile):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    DS = driver.Open(shpfile, 1)
    lyr = DS.GetLayer(0)
    prosrs = lyr.GetSpatialRef()  # 获取投影坐标信息
    # print("投影坐标系为:",prosrs)
    geosrs = prosrs.CloneGeogCS()  # 获取地理坐标系
    # print("地理坐标系为:",geosrs)
    wkt = prosrs.ExportToWkt()  # 将坐标系输出为字符串
    bool1 = wkt.find('UNIT["Metre"')
    bool2 = wkt.find('UNIT["metre"')
    bool3 = wkt.find('UNIT["Meter"')
    if bool1 == -1 and bool2 == -1 and bool3 == -1:
        print('请定义投影坐标！')
        # time.sleep(5)
        os._exit(-1)
    featnumber = lyr.GetFeatureCount()
    for i in range(featnumber):
        feature = lyr.GetFeature(i)
        geo = feature.GetGeometryRef()
        num_point = geo.GetPointCount()
        x = np.arange(num_point)
        y = np.arange(num_point)
        for j in range (num_point):
            x[j] = geo.GetX(j)
            y[j] = geo.GetY(j)
        arr = np.dstack((x,y))
        arr = arr.reshape(num_point,2)
        return arr

def length_addfield(shpfile,length):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    DS = driver.Open(shpfile,0)
    lyr = DS.GetLayer()
    prosrs = lyr.GetSpatialRef()   #获取投影坐标信息

    new_field = ogr.FieldDefn("Length", ogr.OFTReal)
    new_field.SetWidth(32)
    new_field.SetPrecision(2)  # 设置长度精度
    lyr.CreateField(new_field)
    featnumber = lyr.GetFeatureCount()

    for i in range(featnumber):
        feature = lyr.GetFeature(i)
        geom = feature.GetGeometryRef()
        # print(geom)
        area = geom.GetArea()
        length = length / 1000  #长度为千米
        feature.SetField("Length", length)  # 将面积添加到属性表中
        lyr.SetFeature(feature)

    poly_DS = None





def lenth_sta(array_point):
    point_edge = len(array_point)-1
    length = []
    for i in range(point_edge):
        ax,ay = array_point[i]
        bx,by = array_point[i+1]
        length.append(math.hypot(bx-ax,by-ay)) #求两个点的距离，math.hypot为求平方根函数
    length_sum = np.sum(length)
    return length_sum


if __name__ == '__main__':
    # if len(sys.argv) != 2:
    #     distutils.log.error("not enougth input parameters")
    #     sys.exit(-1)

    shppath = r'D:/AAdata/潮间带提取数据/final_data/Area1/line'




    os.chdir(shppath)
    for root, dirs, files in os.walk(shppath):
        for file in files:

            last_name = file[-3:]
            if last_name == 'shp':
                filepath = os.path.join(root,file)
                array = geopoint_advanced(filepath)
                length = lenth_sta(array)
                length_addfield(filepath,length)
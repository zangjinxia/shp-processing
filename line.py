'''
@author zangjinxia
@created 20201203
@brief 一些矢量操作的基本函数，包括面擦除、相交，创建矢量，复制矢量，
东西向平移矢量，点坐标输出，经纬度和投影坐标互相转换，线面互转等处理
'''

import sys
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
import numpy as np
from numpy import double
# import shapely
import os


def polyErase(path1,path2,outpath):
    """
用第一个面擦除第二个面
    :param path1: 第一个多边形面
    :param path2: 第二个多边形面
    :param outpath: 输出的擦除面
    """

    #打开两个面矢量文件
    driver = ogr.GetDriverByName('ESRI Shapefile')
    poly_DS = driver.Open(path1)
    poly_lyr = poly_DS.GetLayer(0)
    poly_feature = poly_lyr.GetFeature(0)
    poly_geom = poly_feature.GetGeometryRef()
    # vp.plot(poly_geom,fill = False,ec = 'red',ls = 'dashed',lw = 3)
    # Dif_geom = high_geom.Difference(poly_geom)

    high = driver.Open(path2,0)
    if high is None:
        print ('could not open')
        sys.exit(1)
    print ('done!')
    #一般矢量文件只有一个图层，打开第一个图层
    high_lyr = high.GetLayer(0)
    high_feature = high_lyr.GetFeature(0)
    # high_geom = high_lyr.GetGeometryRef()
    #创建面
    outDs = driver.CreateDataSource(outpath)
    if outDs is None:
        print("Could not creat file")
        sys.exit(1)

    srs = high_lyr.GetSpatialRef()
    outlayer = outDs.CreateLayer('out',srs,geom_type = ogr.wkbPolygon)
    high_lyr.Erase(poly_lyr, outlayer)
    poly_DS.Destroy()
    high.Destroy()
    outDs.Destroy()


def polyintersection(path1, path2, outpath):
    """
求两个多边形面的交集
    :param path1: 第一个多边形面
    :param path2: 第二个多边形面
    :param outpath: 输出的交集面
    """

    # 打开两个面矢量文件
    # path1 = r'D:/yanshuixian.shp'
    # path2 = r'D:\AAdata\关岛\2019\LC08_L1TP_100051_20190731_20190819_01_T1\process\淹水线\test.shp'
    # outpath = r'D:/result.shp'

    driver = ogr.GetDriverByName('ESRI Shapefile')
    poly_DS = driver.Open(path1)
    poly_lyr = poly_DS.GetLayer(0)
    poly_feature = poly_lyr.GetFeature(0)
    poly_geom = poly_feature.GetGeometryRef()
    # vp.plot(poly_geom,fill = False,ec = 'red',ls = 'dashed',lw = 3)
    # Dif_geom = high_geom.Difference(poly_geom)

    high = driver.Open(path2, 0)
    if high is None:
        print('could not open')
        sys.exit(1)
    print('done!')
    # 一般矢量文件只有一个图层，打开第一个图层
    high_lyr = high.GetLayer(0)
    high_feature = high_lyr.GetFeature(0)
    # high_geom = high_lyr.GetGeometryRef()
    # 创建面
    outDs = driver.CreateDataSource(outpath)
    if outDs is None:
        print("Could not creat file")
        sys.exit(1)

    srs = high_lyr.GetSpatialRef()
    outlayer = outDs.CreateLayer('out', srs, geom_type=ogr.wkbPolygon)
    high_lyr.Intersection(poly_lyr, outlayer)
    poly_DS.Destroy()
    high.Destroy()
    outDs.Destroy()
#----------------------------------------------------#
#创建线矢量
def creatline():
    line = ogr.Geometry(ogr.wkbLineString)
    line.AddPoint(54,37)
    line.AddPoint(62,35.5)
    line.AddPoint(70.5,38)
    line.AddPoint(74.5,41.5)
    print(line)
    for i in range(line.GetPointCount()):
        line.SetPoint(i,line.GetX(i),line.GetY(i)+1)
    print(line)
    
#创建新矢量文件
def creatshp(path,type):
    ds = driver.CreateDataSource('buffer.shp')
    layer2 = ds.CreateLayer('buffer',type=ogr.wkbPolygon)
    fieldDefn = ogr.FieldDefn('id', ogr.OFTString)  #添加字段
    fieldDefn.SetWidth(4)
    layer2.CreateField(fieldDefn)
    featureDefn = layer2.GetLayerDefn() #创建一个feature
    feature = ogr.Feature(featureDefn)
    feature.SetGeometry()
    feature.SetField('id', 23)
    layer2.CreateFeature(feature)

    


def copyshp(inpath,outpath):
    """
    inpath:作为基准的矢量路径
    outpath:输出的矢量路径

    """
    driver = ogr.GetDriverByName('ESRI Shapefile')
    inDs = driver.Open(inpath)
    if inDs is None:
        print("Could not open",inpath)
        sys.exit(1)
    inLayer = inDs.GetLayer()

    #检查需创建矢量是否已存在
    if os.path.exists(outpath):
        driver.DeleteDataSource(outpath)
    #创建矢量
    outDs = driver.CreateDataSource(outpath)
    if outDs is None:
        print("Could not creat file")
        sys.exit(1)
    #创建图层
    outLayer = outDs.CreateLayer('move', geom_type = ogr.wkbMultiLineString)

    #将输入矢量的属性应用到新矢量
    fieldList = []
    fieldList =  getfield(inLayer)
    print(fieldList)
    fieldDefn = inLayer.GetFeature(0).GetFieldDefnRef('id')
    outLayer.CreateField(fieldDefn)
    featureDefn = outLayer.GetLayerDefn() #定义要素

    cnt = 0
    inFeature = inLayer.GetNextFeature()
    while inFeature:
        outFeature = ogr.Feature(featureDefn)
        geo = inFeature.GetGeometryRef()
        outFeature.SetGeometry(geo)
        outLayer.CreateFeature(outFeature)
        inFeature.Destroy()
        outFeature.Destroy()
        cnt = cnt + 1
        if cnt < 6:
            inFeature = inLayer.GetNextFeature()
        else:
            break

    inDs.Destroy()
    outDs.Destroy()


def moveshp(inpath,outpath,moveDis):
    """
    实现线矢量东西向平移
    inpath:作为基准的矢量路径
    outpath:输出的矢量路径
    moveDis:平移距离

    """
    driver = ogr.GetDriverByName('ESRI Shapefile')
    inDs = driver.Open(inpath)
    if inDs is None:
        print("Could not open",inpath)
        sys.exit(1)
    inLayer = inDs.GetLayer()

    #检查需创建矢量是否已存在
    if os.path.exists(outpath):
        driver.DeleteDataSource(outpath)
    #创建矢量
    outDs = driver.CreateDataSource(outpath)
    if outDs is None:
        print("Could not creat file")
        sys.exit(1)
    #创建图层
    outLayer = outDs.CreateLayer('move', geom_type = ogr.wkbMultiLineString)

    #将输入矢量的属性应用到新矢量
    fieldList = []
    fieldList =  getfield(inLayer)
    print(fieldList)
    fieldDefn = inLayer.GetFeature(0).GetFieldDefnRef('id')
    outLayer.CreateField(fieldDefn)
    featureDefn = outLayer.GetLayerDefn()

    cnt = 0
    inFeature = inLayer.GetNextFeature()
    while inFeature:
        outFeature = ogr.Feature(featureDefn)
        # geo = inFeature.GetGeometryRef()
        featnumber = inLayer.GetFeatureCount()


        geo = inFeature.GetGeometryRef()
        num_point = geo.GetPointCount()
        for j in range(num_point):
            geo.SetPoint(j, geo.GetX(j) + moveDis, geo.GetY(j))
        outFeature.SetGeometry(geo)
        outLayer.CreateFeature(outFeature)
        inFeature.Destroy()
        outFeature.Destroy()
        cnt = cnt + 1
        if cnt < 6:
            inFeature = inLayer.GetNextFeature()
        else:
            break

    inDs.Destroy()
    outDs.Destroy()

def moveshp_improve(inpath,outpath,moveDis):
    """
    实现线矢量东西向平移
    inpath:作为基准的矢量路径
    outpath:输出的矢量路径
    moveDis:平移距离

    """
    driver = ogr.GetDriverByName('ESRI Shapefile')
    inDs = driver.Open(inpath)
    if inDs is None:
        print("Could not open",inpath)
        sys.exit(1)
    inLayer = inDs.GetLayer()

    #检查需创建矢量是否已存在
    if os.path.exists(outpath):
        driver.DeleteDataSource(outpath)
    #创建矢量
    outDs = driver.CreateDataSource(outpath)
    if outDs is None:
        print("Could not creat file")
        sys.exit(1)
    #创建图层
    outLayer = outDs.CreateLayer('move', geom_type = ogr.wkbMultiLineString)

    #将输入矢量的属性应用到新矢量
    fieldList = []
    fieldList =  getfield(inLayer)
    print(fieldList)
    fieldDefn = inLayer.GetFeature(0).GetFieldDefnRef('id')
    outLayer.CreateField(fieldDefn)
    featureDefn = outLayer.GetLayerDefn()

    cnt = 0
    inFeature = inLayer.GetNextFeature()
    while inFeature:
        outFeature = ogr.Feature(featureDefn)
        # geo = inFeature.GetGeometryRef()
        featnumber = inLayer.GetFeatureCount()


        geo = inFeature.GetGeometryRef()
        num_point = geo.GetPointCount()
        for j in range(num_point):
            geo.SetPoint(j, geo.GetX(j) + moveDis, geo.GetY(j))
        outFeature.SetGeometry(geo)
        outLayer.CreateFeature(outFeature)
        inFeature.Destroy()
        outFeature.Destroy()
        cnt = cnt + 1
        if cnt < 6:
            inFeature = inLayer.GetNextFeature()
        else:
            break

    inDs.Destroy()
    outDs.Destroy()

#------------------------------------------------------------------------#
#getfield函数得到该图层的属性字段，即属性表中的表头,表头名以列表形式存放
#输入参数：图层
def getfield(layer):
    schema=[]  # 定义列表盛放当前图层的属性字段
    
    ldefn= layer.GetLayerDefn()
    
    for n in range(ldefn.GetFieldCount()):
    
        fdefn = ldefn.GetFieldDefn(n)
    
        schema.append(fdefn.name)

    return schema
    print(f'the fields of this layer: {schema}')
    

#---------------------------------------------------------------#
#输出所有点的坐标
def geopoint(lyr):
    for i in range(lyr.GetFeatureCount()):
        feature = lyr.GetFeature(i)
        geo = feature.GetGeometryRef()
        num_point = geo.GetPointCount()
        x = np.arange(num_point)
        y = np.arange(num_point)
        for j in range (num_point):
            x[j] = geo.GetX(j)
            y[j] = geo.GetY(j)
            arr = []

        return(x,y)

#-------------------------------------------------------#
#将线坐标放到一个三维矩阵arr中
def geopoint_advanced(lyr):
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
        return arr
        print(arr)  
        print(arr.shape)  


#将投影坐标转为地理坐标，返回该点的经纬度，是一个三维tuple类型（经度，纬度，0）
def prj2geo(path,x,y):
    ogr.RegisterAll()
    driver = ogr.GetDriverByName('ESRI Shapefile')
    ds = driver.Open(path)
    layer0 = ds.GetLayerByIndex(0)
    prosrs = layer0.GetSpatialRef()
    geosrs = osr.SpatialReference()
    geosrs.SetWellKnownGeogCS("WGS84")
    ct = osr.CoordinateTransformation(prosrs, geosrs)
    coords = ct.TransformPoint(x, y)
    return coords[:2]


def lonlat2geo(dataset, lon, lat):
    '''
    将经纬度坐标转为投影坐标（具体的投影坐标系由给定数据确定）
    :param dataset: GDAL地理数据
    :param lon: 地理坐标lon经度
    :param lat: 地理坐标lat纬度
    :return: 经纬度坐标(lon, lat)对应的投影坐标
    '''
    prosrs, geosrs = getSRSPair(dataset)
    ct = osr.CoordinateTransformation(geosrs, prosrs)
    coords = ct.TransformPoint(lon, lat)
    return coords[:2]



def unionline(path):
    ogr.RegisterAll()
    driver = ogr.GetDriverByName('ESRI Shapefile')
    line = driver.Open(filepath, 0)
    lyr = line.GetLayer()

    for feat in lyr:
        geo = feat.GetGeometryRef()
        print(geo)
        shapely.ops.union(feat)
        # geo.UnionCascaded()
    featnumber = lyr.GetFeatureCount()
    print(featnumber)



def pol2line(polyfn,linefn):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    polyds = ogr.Open(polyfn,0)
    polyLayer = polyds.GetLayer()
    #创建输出文件
    if os.path.exists(linefn):
        driver.DeleteDataSource(linefn)
    lineds =driver.CreateDataSource(linefn)
    linelayer = lineds.CreateLayer(linefn,geom_type = ogr.wkbLineString)
    featuredefn = linelayer.GetLayerDefn()
    #获取ring到几何体
    #geomline = ogr.Geometry(ogr.wkbGeometryCollection)
    for feat in polyLayer:
        geom = feat.GetGeometryRef()
        ring = geom.GetGeometryRef(0)
        #geomcoll.AddGeometry(ring)
        outfeature = ogr.Feature(featuredefn)
        outfeature.SetGeometry(ring)
        linelayer.CreateFeature(outfeature)
        outfeature = None


def linetopoly(filepath,polypath):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    #打开线shp文件
    line = driver.Open(filepath,0)
    if line is None:
        print ('could not open')
        sys.exit(1)
    print ('done!')
    #一般矢量文件只有一个图层，打开第一个图层
    lyr = line.GetLayer()
    srs= lyr.GetSpatialRef()
    print(srs)
    #创建面矢量
    strVectorFile = polypath
    ogr.RegisterAll()
    strDriverName = "ESRI Shapefile"
    oDriver = ogr.GetDriverByName(strDriverName)
    if oDriver == None:
        print("%s 驱动不可用！\n", strDriverName)

    oDS = oDriver.CreateDataSource(strVectorFile)  # 创建数据源
    if oDS == None:
        print("创建文件【%s】失败！", strVectorFile)
    # srspoly = osr.SpatialReference()
    oLayer = oDS.CreateLayer('poly',srs,ogr.wkbPolygon)
    if oLayer == None:
        print("图层创建失败！\n")

    #添加矢量数据
    oFieldID = ogr.FieldDefn("FieldID", ogr.OFTInteger)  # 创建一个叫FieldID的整型属性
    oLayer.CreateField(oFieldID, 1)

    oDefn = oLayer.GetLayerDefn()  # 定义要素

    #创建面
    oFeaturepoly = ogr.Feature(oDefn)
    oFeaturepoly.SetField(0,0) # 第一个参数表示第几个字段，第二个参数表示字段的值

    ring = ogr.Geometry(ogr.wkbLinearRing) #  构建几何类型:线

    #将线中的坐标依次添加到ring中
    featnumber = lyr.GetFeatureCount()
    for i in range(featnumber):
        feature = lyr.GetFeature(i)
        geo = feature.GetGeometryRef()
        num_point = geo.GetPointCount()
        for j in range (num_point):
            ring.AddPoint(geo.GetX(j),geo.GetY(j))   #向ring（线）中添加点

    yard = ogr.Geometry(ogr.wkbPolygon)  #构建几何类型：多边形
    yard.AddGeometry(ring)
    yard.CloseRings()

    geompoly = ogr.CreateGeometryFromWkt(str(yard))   # 将封闭后的多边形集添加到属性表
    oFeaturepoly.SetGeometry(geompoly)
    oLayer.CreateFeature(oFeaturepoly)




# moveshp('D:/201907.shp','D:/move3.shp',-10)

#矢量线文件
filepath = r'D:\2019071.shp'
polypath = r'D:/yanshuixian.shp'

# linepath = r'D:\AAdata\关岛\2019\LC08_L1TP_100051_20190731_20190819_01_T1\process\淹水线\highline.shp'
# pol2line(filepath,linepath)
driver = ogr.GetDriverByName('ESRI Shapefile')
#打开线shp文件
line = driver.Open(filepath,0)
if line is None:
    print ('could not open')
    sys.exit(1)
print ('done!')
#一般矢量文件只有一个图层，打开第一个图层
lyr = line.GetLayer()
# geopoint(lyr)
#打开图层中的第1个要素
feat = lyr.GetFeature(1)
# BOUNDARY = feat.GetBoundary()
# print(BOUNDARY)
# print(feat)
for feat in lyr:
    geo = feat.GetGeometryRef()
    geo.CloseRings()
    print('done')
linetopoly(filepath,polypath)
# geo = lyr.Geometry()
# lyr.UnionCascaded()
#得到该图层的地理坐标系
srs= lyr.GetSpatialRef()
# print(f'the spatial reference system of the data: {srs.ExportToPrettyWkt()}')

#求图层中要素总个数，即属性表中的行数
featnumber = lyr.GetFeatureCount()
corodinate = geopoint_advanced(lyr)
print(corodinate.shape)
# for i in range(featnumber):
#     feature = lyr.GetFeature(i)
#     geo = feature.GetGeometryRef()
#     num_point = geo.GetPointCount()
#     arr_cor = np.empty((featnumber,num_point,num_point))
#     x = np.arange(num_point,dtype=double)
#     y = np.arange(num_point,dtype=double)
#     for j in range (num_point):
#         x[j] = geo.GetX(j)
#         y[j] = geo.GetY(j)
#         arr = prj2geo(filepath, x[j], y[j])
# #         coords = ct.TransformPoint(x[j], y[j])
# # #         print(coords[:2])
#         arr = np.asarray(arr)
#         print(arr[:3])
#     print(arr.shape)
# #     print(arr.shape)
#     feature.Destroy()
#     line.Destroy()
#     print('坐标读取完毕！')
























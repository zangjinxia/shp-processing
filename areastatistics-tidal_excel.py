'''
@brief 统计潮间带（矢量面）的面积信息，将面积写入到excel中
@author zangjinxia
@created 2020-12-03
'''

from osgeo import ogr, osr
import gdal
import sys
import distutils
import os
import time
import xlwt

def area_sta(path):
    driver = ogr.GetDriverByName('ESRI Shapefile')
    poly_DS = driver.Open(path,0)
    poly_lyr = poly_DS.GetLayer()
    prosrs = poly_lyr.GetSpatialRef()   #获取投影坐标信息
    #print("投影坐标系为:",prosrs)
    geosrs = prosrs.CloneGeogCS()    #获取地理坐标系
    #print("地理坐标系为:",geosrs)
    wkt = prosrs.ExportToWkt()     #将坐标系输出为字符串
    bool1 = wkt.find('UNIT["Metre"')
    bool2 = wkt.find('UNIT["metre"')
    bool3 = wkt.find('UNIT["Meter"')
    if bool1 == -1 and bool2 == -1 and bool3 == -1:
        print('请定义投影坐标！')
        # time.sleep(5)
        os._exit(-1)

    # new_field = ogr.FieldDefn("Area", ogr.OFTReal)
    # new_field.SetWidth(32)
    # new_field.SetPrecision(2)  # 设置面积精度
    # poly_lyr.CreateField(new_field)
    featnumber = poly_lyr.GetFeatureCount()
    sum_area = 0
    for i in range(featnumber):
        feature = poly_lyr.GetFeature(i)
        geom = feature.GetGeometryRef()
        #print(geom)
        area = geom.GetArea()
        area = round(area/1000000,2)
        # feature.SetField("Area", area)  # 将面积添加到属性表中
        # poly_lyr.SetFeature(feature)
        sum_area=sum_area+area
    poly_DS = None
    # print(sum_area)
    return sum_area
if __name__ == '__main__':
    # if len(sys.argv) != 2:
    #     distutils.log.error("not enougth input parameters")
    #     sys.exit(-1)
    # shpfile = sys.argv[1]   #shpfile = r'D:/AAdata/测试用矢量面/poly3.shp'
    tidal_path ='D:/AAdata/潮间带提取数据/出图数据/areasta'

    workbook = xlwt.Workbook('D:/AAdata/潮间带提取数据/出图数据/AreaSta.xlsx')  # 创建工作簿
    sheet = workbook.add_sheet('AreaSta')

    os.chdir(tidal_path)
    count = -1
    for root, dirs, files in os.walk(tidal_path):
        for file in files:
            last_name = file[-3:]
            if last_name == 'shp':
                count = count + 1

                filepath = os.path.join(root, file)
                area = area_sta(filepath)
                print(file,area)

                j = 0                                #将数据写入表格
                sheet.write(count,j,file)
                j = j+1
                sheet.write(count,j,area)
                j = 0
    workbook.save('D:/AAdata/潮间带提取数据/出图数据/AreaSta.xlsx')

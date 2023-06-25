import serial
import folium
import math
import struct
import numpy as np
import matplotlib.pyplot as plt
from math import radians, cos, sin, asin, sqrt
import keyboard

la_list = []
lo_list = []
gps_list = []

#修改端口号和波特率
ser = serial.Serial('COM15', 115200,timeout=0)

# 串口接收函数
def gps_receive():
    A_flag = 0
    int_value = 0
    w = 0
    lo_flag = 0
    loop = 0
    if ser.isOpen():
        print("open success")
    else:
        print("open failed")
    while ser.isOpen():
        count = ser.inWaiting()
        if keyboard.is_pressed('q'):
            for i in range(len(lo_list)):
                gps_list.append([lo_list[i], la_list[i]])
            ser.close()
            print("接收完毕!")
        if count > 0:
            data = ser.read(1)
            # print(data)
            if data == b'1':
                # 帧头判断成功，开始分析数据
                A_flag = 1
                lo_flag = 0
                loop = 0
                if len(la_list) > 2:
                    if la_list[-1] == 0 or lo_list[-1] == 0:
                        del la_list[-1],lo_list[-1]
                        if len(la_list) < len(lo_list):
                            min_list = len(la_list)
                        else:
                            min_list = len(lo_list)
                        for i in range(min_list):
                            gps_list.append([lo_list[i], la_list[i]])
                        ser.close()
                        print("接收完毕!")
                        break
                continue
            # 判断帧尾
            if data == b'3':
                w = 0
                float_value = struct.unpack('f', struct.pack('I', int_value))[0]
                lo_list.append(float_value)
                int_value = 0
                # 帧尾判断成功，开始转换数据
                A_flag = 0
                print(len(lo_list))
                loop = 0
                continue
            # 帧头判断成功
            if A_flag == 1:
                # 分析数据，判断是经度，纬度
                if data != b'2':
                    if lo_flag == 0:
                        int_byte = ord(data)
                        int_value = int_value | (int_byte << w)
                        w+=8
                        loop += 1
                    else:
                        int_byte = ord(data)
                        int_value = int_value | (int_byte << w)
                        w += 8
                        loop += 1
                elif data == b'2':
                    w = 0
                    if loop > 4:
                        loop = 0
                        int_value = 0
                        continue
                    float_value = struct.unpack('<f', struct.pack('<I', int_value))[0]
                    la_list.append(float_value)
                    int_value = 0
                    lo_flag = 1
                    loop = 0

            if data == b'4':
                if len(la_list) < len(lo_list):
                    min_list = len(la_list)
                else:
                    min_list = len(lo_list)
                for i in range(min_list):
                    gps_list.append([la_list[i], lo_list[i]])
                ser.close()
                print("接收完毕!")

#n阶贝塞尔曲线生成函数
def bezier_curve(control_points, num_points):
    n = len(control_points) - 1
    t = np.linspace(0, 1, num_points)
    curve_points = np.zeros((num_points, 2))

    for i in range(num_points):
        point = np.array([0.0, 0.0])
        for j in range(n + 1):
            coefficient = np.math.comb(n, j) * t[i]**j * (1 - t[i])**(n - j)
            point += coefficient * control_points[j]
        curve_points[i] = point

    return curve_points

# 获取两个坐标点的距离
def get_distance(lon1, lat1, lon2, lat2):
    # 将十进制度数转化为弧度
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    #     a = sin(dlat/2)*sin(dlat/2) + cos(lat1) * cos(lat2) * sin(dlon/2)*sin(dlon/2)
    #     c = 2 * asin(sqrt(a))
    c = 2 * asin(sqrt(pow(sin(dlat / 2), 2) + cos(lat1) * cos(lat2) * pow(sin(dlon / 2), 2)));  # google maps里面实现的算法
    r = 6378.137  # 地球平均半径，单位为公里
    # print(c * r * 1000)s
    return c * r * 1000

#获取两个坐标点方位角
def get_azimuth(lon1, lat1, lon2, lat2):
    radLatA = math.radians(lat1)
    radLonA = math.radians(lon1)
    radLatB = math.radians(lat2)
    radLonB = math.radians(lon2)
    dLon = lon2 - lon1
    y = math.sin(dLon) * math.cos(radLatB)
    x = math.cos(radLatA) * math.sin(radLatB) - math.sin(radLatA) * math.cos(radLatB) * math.cos(dLon)
    brng = math.degrees(math.atan2(y, x))
    brng = (brng + 360) % 360
    return brng

#计算曲线路径长度
def get_cir(curve_points,num_points):
    cir = 0
    for i in range(int(num_points/2)-1):
        lon1 = curve_points[i][0]
        lat1 = curve_points[i][1]
        lon2 = curve_points[i+1][0]
        lat2 = curve_points[i+1][1]
        cir += get_distance(lon1, lat1, lon2, lat2)

    return cir

# 绘制控制点和贝塞尔曲线
def bezier_draw(control_points,curve_points):
    plt.plot(control_points[:, 0], control_points[:, 1], 'ro-', label='Control Points')
    plt.plot(curve_points[:, 0], curve_points[:, 1], 'b-', label='Bezier Curve')

    plt.axis('equal')
    plt.grid(True)
    plt.legend()
    plt.title('Bezier Curve')
    plt.show()

#将点位导出.txt文件
def out_put(point,speed):
    n = len(point)
    with open("output.txt", "w") as file:
        file.truncate() #清空文本
        file.write("\n*********************la***********************\n")
        for i in range(0,n):
            file.write(str(point[i][1])+',')
            if i%5 == 0 and i!=0:
                file.write("\n")
        file.write("\n*********************lo***********************\n")
        for i in range(0,n):
            file.write(str(point[i][0])+',')
            if i%5 == 0 and i!=0:
                file.write("\n")
        file.write("\n******************velocity*********************\n")
        for i in range(0,n):
            file.write(str(speed[i])+',')
            if i%5 == 0 and i!=0:
                file.write("\n")
        print("Write_OK!")

# 计算曲率
def compute_curvature(points):

    # 计算一阶导数（速度向量）
    first_derivative = np.gradient(points, axis=0)

    # 计算二阶导数（加速度向量）
    second_derivative = np.gradient(first_derivative, axis=0)

    # 计算速度向量的模长（即速度的大小）：
    magnitude = np.linalg.norm(first_derivative, axis=1)

    # 计算曲率：
    curvature = np.linalg.norm(second_derivative, axis=1) / magnitude ** 3

    return curvature

#速度规划
def speed_control(points):
    value = 6.4e+08 #曲率的阈值，可以观察打印出来的曲率数组修改
    velocity = np.array([])
    curvature = compute_curvature(points)
    n = len(curvature)
    keep = np.ones(len(points), dtype=bool)
    keep_s = np.ones(len(points), dtype=bool)
    keep_s[0] = True
    for i in range(n):
        point_curvature = curvature[i]
        if point_curvature < value and 0 <i< n-2: #根据曲率滤掉一些直道的点
            straight_flag = 1
            keep[i] = False
            if i != n-1 and i>0:
                keep_s[i-1] = False
        elif i<=1 or i>=n-1:
            straight_flag = 1
        else:
            straight_flag = 0

        if straight_flag == 1:
            velocity = np.append(velocity,7)  # 直道速度
        else:
            velocity = np.append(velocity,5)  # 弯道速度

    points = points[keep]
    velocity = velocity[keep_s]

    return points,velocity #返回过滤后的点位数组和速度数组

if __name__ == '__main__':
    # gps_receive()
    gps_list=[[110.29784393310547, 21.153764724731445], [110.29788970947266, 21.15373992919922],
             [110.29791259765625, 21.15373992919922], [110.29792022705078, 21.153743743896484],
             [110.29793548583984, 21.15374755859375], [110.29793548583984, 21.15373420715332],
             [110.29793548583984, 21.15372085571289], [110.29793548583984, 21.153705596923828],
             [110.2979507446289, 21.15370750427246], [110.29796600341797, 21.15372085571289],
             [110.2979736328125, 21.153722763061523], [110.29798126220703, 21.153718948364258],
             [110.29798126220703, 21.15370750427246], [110.2979965209961, 21.153696060180664],
             [110.29801177978516, 21.153701782226562], [110.29801177978516, 21.153715133666992],
             [110.29785919189453, 21.153789520263672]]
    control_points = np.array(gps_list)  # 控制点坐标

    num_points = len(control_points) + 10  # 曲线上的点数量，如发现点位重合情况可适当改小

    curve_points = bezier_curve(control_points, num_points)

    qulv = compute_curvature(curve_points)
    print("曲率数组为:",qulv)
    print("GPS点位为:", gps_list)

    filter_points,velocity = speed_control(curve_points)
    print("速度数组为:",velocity)
    out_put(filter_points,velocity)

#修改下面这个函数的第一个参数来查看原始点位(control_points)或处理后的点位(filter_points)
    bezier_draw(control_points,curve_points)


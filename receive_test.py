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
GPS_get_latitude = []
GPS_get_longitude = []

target_point = 0

ser = serial.Serial('COM15', 115200,timeout=0)

# ���ڽ��պ���
def gps_receive():
    A_flag = 0
    lo_flag = 0
    int_value = 0
    w = 0
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
            print("�������!")
        if count > 0:
            data = ser.read(1)
            # print(data)
            if data == b'1':
                # ֡ͷ�жϳɹ�����ʼ��������
                A_flag = 1
                lo_flag = 0
                loop = 0
                # if len(la_list) > 2:
                #     if la_list[-1] == 0 or lo_list[-1] == 0:
                #         del la_list[-1],lo_list[-1]
                #         if len(la_list) < len(lo_list):
                #             min_list = len(la_list)
                #         else:
                #             min_list = len(lo_list)
                #         for i in range(min_list):
                #             gps_list.append([lo_list[i], la_list[i]])
                #         ser.close()
                #         print("�������!")
                #         break
                continue
            # �ж�֡β
            if data == b'3':
                w = 0
                float_value = struct.unpack('f', struct.pack('I', int_value))[0]
                lo_list.append(float_value)
                int_value = 0
                # ֡β�жϳɹ�����ʼת������
                A_flag = 0
                print(len(lo_list))
                loop = 0
                continue
            # ֡ͷ�жϳɹ�
            if A_flag == 1:
                # �������ݣ��ж��Ǿ��ȣ�γ��
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
                    gps_list.append([lo_list[i], la_list[i]])
                ser.close()
                print("�������!")

#n�ױ������������ɺ���
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
        GPS_get_latitude.append(curve_points[i][0])
        GPS_get_longitude.append(curve_points[i][1])

    return curve_points

# ��ȡ���������ľ���
def get_distance(lon1, lat1, lon2, lat2):
    # ��ʮ���ƶ���ת��Ϊ����
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine��ʽ
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    #     a = sin(dlat/2)*sin(dlat/2) + cos(lat1) * cos(lat2) * sin(dlon/2)*sin(dlon/2)
    #     c = 2 * asin(sqrt(a))
    c = 2 * asin(sqrt(pow(sin(dlat / 2), 2) + cos(lat1) * cos(lat2) * pow(sin(dlon / 2), 2)));  # google maps����ʵ�ֵ��㷨
    r = 6378.137  # ����ƽ���뾶����λΪ����
    # print(c * r * 1000)s
    return c * r * 1000

#��������·������
def get_cir(curve_points,num_points):
    cir = 0
    for i in range(int(num_points/2)-1):
        lon1 = curve_points[i][0]
        lat1 = curve_points[i][1]
        lon2 = curve_points[i+1][0]
        lat2 = curve_points[i+1][1]
        cir += get_distance(lon1, lat1, lon2, lat2)

    return cir

# ���ƿ��Ƶ�ͱ���������
def bezier_draw(control_points,curve_points):
    plt.plot(control_points[:, 0], control_points[:, 1], 'ro-', label='Control Points')
    plt.plot(curve_points[:, 0], curve_points[:, 1], 'b-', label='Bezier Curve')

    plt.axis('equal')
    plt.grid(True)
    plt.legend()
    plt.title('Bezier Curve')
    plt.show()

#����λ����.txt�ļ�
def out_put(GPS_get_longitude,GPS_get_latitude):
    if len(GPS_get_longitude) < len(GPS_get_latitude):
        min_list = len(GPS_get_longitude)
    else:
        min_list = len(GPS_get_latitude)
    with open("output.txt", "w") as file:
        file.truncate() #����ı�
        file.write("\n*********************lo***********************\n")
        for i in range(0,min_list):
            file.write(str(GPS_get_longitude[i])+',')
            if i%5 == 0 and i!=0:
                file.write("\n")
        file.write("\n*********************la***********************\n")
        for i in range(0,min_list):
            file.write(str(GPS_get_latitude[i])+',')
            if i%5 == 0 and i!=0:
                file.write("\n")
        print("Write_OK!")

if __name__ == '__main__':
    gps_receive()
    control_points = np.array(gps_list)  # ���Ƶ�����
    num_points = len(control_points) + 50  # �����ϵĵ�����

    curve_points = bezier_curve(control_points, num_points)

    dis = get_cir(curve_points,num_points)
    print("GPS��λΪ:", gps_list)
    print("����Ϊ:", dis)

    # print(curve_points)
    out_put(GPS_get_longitude,GPS_get_latitude)

    bezier_draw(control_points, curve_points)

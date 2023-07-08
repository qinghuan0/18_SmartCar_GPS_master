# -------------------------------
# text_operation.py
# author:恩
# version:4.2
# -------------------------------

import serial
import struct
import keyboard
import easygui as g
import numpy as np
from time import sleep

def gps_receive(ser):
    A_flag = 0
    int_value = 0
    w = 0
    lo_flag = 0
    loop = 0
    lo_list = []
    la_list = []
    flag_num = 0
    flag_point = 0
    if ser.isOpen():
        print("open success")
    else:
        print("open failed")
    while ser.isOpen():
        count = ser.inWaiting()
        if keyboard.is_pressed('q'):
            ser.close()
            print("接收完毕!")
            break
        if count > 0:
            data = ser.read(1)
            print(data)
            if data == b'1':
                # 帧头判断成功，开始分析数据
                A_flag = 1
                lo_flag = 0
                loop = 0
                # if len(la_list) > 2:
                    # if la_list[-1] == 0 or lo_list[-1] == 0:
                    #     del la_list[-1],lo_list[-1]
                    #     ser.close()
                    #     print("接收完毕!")
                    #     break
                continue
            # 判断帧尾
            if data == b'3':
                w = 0
                if flag_point == 1: #标志点
                    flag_num += 1
                float_value = struct.unpack('f', struct.pack('I', int_value))[0]
                lo_list.append(float_value)
                int_value = 0
                # 帧尾判断成功，开始转换数据
                A_flag = 0
                # print(len(lo_list))
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
                flag_point = 1

            if data == b'5':
                ser.close()
                print("接收完毕!")

    flag_lo = lo_list[-flag_num:]
    flag_la = la_list[-flag_num:]
    del lo_list[-flag_num:]
    del la_list[-flag_num:]

    lo_np = np.array(lo_list)
    la_np = np.array(la_list)
    flo_np = np.array(flag_la)
    fla_np = np.array(flag_lo)

    lo_np = np.delete(lo_np,np.where(lo_np == 0))
    la_np = np.delete(la_np,np.where(la_np == 0))
    flo_np = np.delete(flo_np,np.where(flo_np == 0))
    fla_np = np.delete(fla_np,np.where(fla_np == 0))

    return lo_np,la_np,flo_np,fla_np

def txt_out(x, y, flag_x, flag_y, your_name):
    # -----------save---txt--------------
    # 输出限制在小数点后6位
    # for i in range(len(x)):
    #     x[i] = round(x[i], 6)
    #     y[i] = round(y[i], 6)
    # for i in range(len(flag_x)):
    #     flag_x[i] = round(flag_x[i], 6)
    #     flag_y[i] = round(flag_y[i], 6)

    n = len(x)
    nn = len(flag_y)
    mystr = ''
    flag_str = ''
    for i in range(n):
        mystr = mystr + str(x[i]) + ','
        mystr = mystr + str(y[i]) + '\n'

    for i in range(nn):
        flag_str = flag_str + str(flag_x[i]) + ','
        flag_str = flag_str + str(flag_y[i]) + '\n'

    with open(your_name, "w") as g:
        g.write(mystr+'***\n'+flag_str)

def read_point(file_name):
    # 数据存放
    data = []
    flag = 0

    with open(file_name, "r") as f:
        for line in f.readlines():
            line = line.strip('\n')
            line = line.strip()
            data.append(line)

    # 读出经纬度数据
    x = []
    y = []
    #标志点
    flg_x = []
    flg_y = []

    for dd in data:
        if dd == '***':
            flag = 1
            continue
        dt = dd.split(',')
        if flag == 0:
            x.append(float(dt[0]))
            y.append(float(dt[1]))

        else:
            flg_x.append(float(dt[0]))
            flg_y.append(float(dt[1]))

    return x, y, flg_x, flg_y

# ---------------生成程序函数-------------------------
def make_code(x, y, speed ,your_name):
    # -----------save---txt--------------
    n = len(x)
    with open(your_name, "w") as file:
        file.truncate()  # 清空文本
        file.write("/*\n"
"* GPS_Point.h\n"
"*\n"
"*  Created on: 2023年6月10日\n"
"*      Author: 恩\n"
"*/\n"
"\n"
"\n"
"#ifndef CODE_GPS_POINT_H_\n"
"#define CODE_GPS_POINT_H_\n"
"\n"
"double lo_bezier[] = {\n")
        for i in range(0, n):
            x[i] = round(x[i],6)
            file.write(str(x[i]) + ',')
            if i % 8 == 0 and i != 0:
                file.write("\n")
        file.write("\n};\n"
                   "double la_bezier[] = {\n")
        for i in range(0, n):
            y[i] = round(y[i], 6)
            file.write(str(y[i]) + ',')
            if i % 8 == 0 and i != 0:
                file.write("\n")
        file.write("\n};\n"
                   "int Speed[] = {\n")
        for i in range(0, n):
            file.write(str(speed[i]) + ',')
            if i % 8 == 0 and i != 0:
                file.write("\n")
        file.write("\n};\n")
        file.write("\n#endif /* CODE_GPS_POINT_H_ */\n")

def make_map(x, y, flg_x, flg_y, your_name):
    n = len(x)
    n_f = len(flg_x)
    with open(your_name, "w") as file:
        for i in range(0, n):
            x[i] = round(x[i], 6)
            y[i] = round(y[i], 6)
            file.write(str(x[i]) + ',')
            file.write(str(y[i]) + '\n')
        file.write("***\n")
        for i in range(0, n_f):
            flg_x[i] = round(flg_x[i], 6)
            flg_y[i] = round(flg_y[i], 6)
            file.write(str(flg_x[i]) + ',')
            file.write(str(flg_y[i]) + '\n')

def bluetooth_out(x, y, speed, your_name):
    for i in range(len(x)):
        x[i] = round(x[i], 6)
        y[i] = round(y[i], 6)
    n = len(x)
    lo_str = ''
    la_str = ''
    speed_str = ''
    for i in range(n):
        lo_str = lo_str + str(x[i]) + ','
        la_str = la_str + str(y[i]) + ','
        speed_str = speed_str + str(speed[i]) + ','

    with open(your_name, "w") as g:
        g.write('***\n'+lo_str+'\n***\n'+la_str+'\n***\n'+speed_str+'\n***')

def bt_read(file_name):
    #读点
    data = []
    flg = 0
    with open(file_name, "r") as f:
        for line in f.readlines():
            line = line.strip('\n')
            line = line.strip()
            line = line.strip(', ')
            data.append(line)

    x = []
    y = []
    z = []
    for dd in data:
        if dd == '***':
            flg = flg+1
            continue
        dt = dd.split(',')
        if flg == 1:
            x = dt
        if flg == 2:
            y = dt
        if flg == 3:
            z = dt

    lo = []
    la = []
    speed = []
    for i in range(len(x)):
        lo.append(float(x[i]))
        la.append(float(y[i]))
        speed.append(int(z[i]))

    return x, y, z

def point_receive(COM):
    # 修改端口号和波特率
    ser = serial.Serial(COM, 115200, timeout=0)
    sleep(0.1)
    lo, la, flag_lo, flag_la= gps_receive(ser)

    outname = g.enterbox("请输入生成文件名：", 'gps-system', 'rec_1')
    if outname != None:
        txt_out(lo, la, flag_lo, flag_la, outname + '.txt')
        # g.msgbox('成功生成代码，请在当前文件夹下查看', "gps-system")

def point_sent(COM,file_name):
    ser = serial.Serial(COM, 115200, timeout=0)
    if ser.isOpen():
        print("open success")
    else:
        print("open failed")
    lo, la, speed = bt_read(file_name)
    flg = 1
    while flg:
        ser.write(b'*')
        for i in range(len(lo)):
            ser.write(lo[i].encode())
            ser.write(b',')
            sleep(0.08)
            print('lo', i)
        ser.write(b'*')
        for i in range(len(lo)):
            ser.write(la[i].encode())
            ser.write(b',')
            sleep(0.08)
            print('la', i)
        ser.write(b'*')
        for i in range(len(lo)):
            ser.write(speed[i].encode())
            ser.write(b',')
            sleep(0.08)
            print('speed', i)

        print('lo',len(lo))
        print('la',len(la))
        print('speed',len(speed))

        print('发送完毕')
        flg = 0

if __name__ == "__main__":
    point_receive('com15')
    # point_sent('com15','bt_out1.txt')


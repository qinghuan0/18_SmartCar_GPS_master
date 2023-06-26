import serial
import folium
import struct
import keyboard
import easygui as g
import numpy as np

#修改端口号和波特率
ser = serial.Serial('COM15', 115200,timeout=0)

def gps_receive():
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
    for i in range(len(x)):
        x[i] = round(x[i], 6)
        y[i] = round(y[i], 6)
    for i in range(len(flag_x)):
        flag_x[i] = round(flag_x[i], 6)
        flag_y[i] = round(flag_y[i], 6)

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

if __name__ == "__main__":
    lo, la, flag_lo, flag_la= gps_receive()

    outname = g.enterbox("请输入生成文件名：", 'gps-system', 'rec_1')
    if outname != None:
        txt_out(lo, la, flag_lo, flag_la, outname + '.txt')
        g.msgbox('成功生成代码，请在当前文件夹下查看', "gps-system")



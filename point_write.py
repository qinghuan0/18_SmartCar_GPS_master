import serial
import folium
import struct
import keyboard
import easygui as g

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
            # print(data)
            if data == b'1':
                # 帧头判断成功，开始分析数据
                A_flag = 1
                lo_flag = 0
                loop = 0
                if len(la_list) > 2:
                    if la_list[-1] == 0 or lo_list[-1] == 0:
                        del la_list[-1],lo_list[-1]
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
                ser.close()
                print("接收完毕!")

    return lo_list,la_list

def txt_out(x, y, your_name):
    # -----------save---txt--------------
    # 输出限制在小数点后6位
    for i in range(len(x)):
        x[i] = round(x[i], 7)
        y[i] = round(y[i], 7)

    n = len(x)
    mystr = ''
    for i in range(n):
        mystr = mystr + str(x[i]) + ','
        mystr = mystr + str(y[i]) + '\n'

    with open(your_name, "w") as g:
        g.write(mystr)

if __name__ == "__main__":
    lo,la = gps_receive()

    outname = g.enterbox("请输入生成文件名：", 'gps-system', 'rec_1')
    if outname != None:
        txt_out(lo, la, outname + '.txt')
        g.msgbox('成功生成代码，请在当前文件夹下查看', "gps-system")



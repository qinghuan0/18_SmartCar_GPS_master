import sys
import os
import matplotlib.pyplot as plt
import numpy as np
from map import Map
from fusion import *
from text_operation import *

# --------------------拟合曲线函数----------------------------
def make_curve(x, y, num):
    # list转numpy
    use_x = np.array(x)
    use_y = np.array(y)

    # 去掉重复的点
    okay = np.where(np.abs(np.diff(use_x)) + np.abs(np.diff(use_y)) > 0)
    use_xx = np.r_[use_x[okay], x[-1]]
    use_yy = np.r_[use_y[okay], y[-1]]

    tck, u = interpolate.splprep([use_xx, use_yy], s=0)
    # evaluate the spline fits for 1000 evenly spaced distance values
    xi, yi = interpolate.splev(np.linspace(0, 1, num), tck)

    return xi, yi

def point_speed(curve_x, curve_y, flg_x, flg_y):
    speed = []
    speed_flg = -1
    for i in range(len(curve_x)):
        if [curve_x[i], curve_y[i]] == [flg_x[0], flg_y[0]]:
            speed_flg = -speed_flg
        if speed_flg == 1:
            speed.append(z_speed)
        elif speed_flg == -1:
            speed.append(s_speed)
        if speed[i] == z_speed and speed[i-1] == s_speed:
            speed[i] = j_speed

    return speed

if __name__ == "__main__":
    setname = ''
    while (os.path.exists(setname + '.txt') != True):
        setname = g.enterbox("请输入采取的gps文件：", 'gps-system', 'test_1')
        if setname == None:
            setname = ''
        else:
            if os.path.exists(setname + '.txt') != True:
                g.msgbox("请确定你的路径下是否有该配置文件！！！", "gps-system")

    x, y, flag_x, flag_y = read_point(setname + ".txt")
    outname = None

    ox, oy = make_curve(x, y, len(x) + 20)
    speed_control = point_speed(ox, oy, flag_x, flag_y)

    print(len(ox))

    fig1, ax1 = plt.subplots()
    ax1.plot(ox, oy, 'go-')
    ax1.plot(x,y,'r-')

    for i in range(0,len(speed_control)):
        if speed_control[i] == z_speed:
            ax1.plot(ox[i],oy[i], 'yo')
        if speed_control[i] == j_speed:
            ax1.plot(ox[i], oy[i], 'co')

    plt.show()

    while True:
        msg = "请选择你的操作"
        title = "gps-system"
        choices = ["开始拟合", "蓝牙发送","退出系统"]
        choice = g.choicebox(msg, title, choices)

        if choice == '退出系统':
            sys.exit(0)  # 如果退出

        if choice == '开始拟合':
            ox, oy = make_curve(x, y, len(x) + 20)
            speed_control = point_speed(ox, oy, flag_x, flag_y)

            print(len(ox))

            fig1, ax1 = plt.subplots()
            ax1.plot(ox, oy, 'go-')
            ax1.plot(x, y, 'r-')

            for i in range(0, len(speed_control)):
                if speed_control[i] == z_speed:
                    ax1.plot(ox[i], oy[i], 'yo')
                if speed_control[i] == j_speed:
                    ax1.plot(ox[i], oy[i], 'co')

            plt.show()

        if choice == '蓝牙发送':
            outname = g.enterbox("请输入生成文件名：", 'gps-system', 'bt_5.0_out1')
            if outname != None:
                bluetooth_out(ox, oy, speed_control,outname + '.txt')
            point_sent('com8', outname + '.txt')
            g.msgbox('发送完毕！')

# -------------------------------
# GPS_master.py
# author:恩
# version:4.2
# -------------------------------

import sys
import os
from map import Map
from fusion import *
from text_operation import *

if __name__ == "__main__":
    # ------------输入地图--------------------
    setname = ''
    while (os.path.exists(setname + '.txt') != True):
        setname = g.enterbox("请输入采取的gps文件：", 'gps-system', 'rec_1')
        if setname == None:
            setname = ''
        else:
            if os.path.exists(setname + '.txt') != True:
                g.msgbox("请确定你的路径下是否有该配置文件！！！", "gps-system")

    #输入模式
    model_choose = g.buttonbox(msg='请输入模式', title=' ', choices=['坡道--圆环_s弯', 's弯--圆环_坡道', 's弯_圆环--坡道'], )

    #输入锥桶个数
    bar_num = int(g.enterbox(msg='锥桶个数', title=' ', default='4', strip=True, image=None, root=None))
    # 读点
    x, y, flag_x, flag_y = read_point(setname + ".txt")
    b_x, b_y, outx, outy, speed_control = Map.out(Map, x, y, flag_x, flag_y, bar_num, model_choose)
    outname = None

    # --------------------------取点完成------------------------------
    # 复制一份留着复位使用
    routx = flag_x.copy()
    routy = flag_y.copy()

    fig1, ax1 = plt.subplots()
    for i in range(len(flag_x)):
        ax1.plot(flag_x[i], flag_y[i], 'bo')
        if i < len(flag_x):
            ax1.text(flag_x[i] + 0.000005, flag_y[i] + 0.000005, str(i), weight="bold", color="k", fontsize=7)

    ax1.plot(outx, outy, 'ro-')
    ax1.plot(b_x, b_y, 'y-')
    # ax1.plot(x[1:3], y[1:3], 'b-')
    for i in range(0,len(speed_control)):
        if speed_control[i] == z_speed:
            ax1.plot(outx[i],outy[i], 'yo')
        if speed_control[i] == j_speed:
            ax1.plot(outx[i], outy[i], 'co')

    plt.xlim(min(outx) - 0.00002, max(outx) + 0.00002)
    plt.ylim(min(outy) - 0.00002, max(outy) + 0.00002)

    plt.show()
    # myplot_NEU(outx, outy, b_x, b_y)

    while True:
        msg = "请选择你的操作"
        title = "gps-system"
        choices = ["修改点位","点位复位","开始拟合","输出代码", "输出地图", "蓝牙发送","退出系统"]
        choice = g.choicebox(msg, title, choices)

        if choice == '修改点位':
            mygps = Point_Move(x, y, flag_x, flag_y)

        if choice == '点位复位':
            flag_x = routx
            flag_y = routy
            routx = flag_x.copy()
            routy = flag_y.copy()
            mygps = Point_Move(x, y, flag_x, flag_y)

        if choice == '输出代码':
            outname = g.enterbox("请输入生成文件名：", 'gps-system', 'out1')
            if outname != None:
                make_code(outx, outy, speed_control,outname + '.txt')
                sys.exit(0)
                # g.msgbox('成功生成代码，请在当前文件夹下查看', "gps-system")

        if choice == '输出地图':
            outname = g.enterbox("请输入生成文件名：", 'gps-system', 'p__y_s_right_d')
            if outname != None:
                make_map(x, y, flag_x, flag_y, outname + '.txt')
                # g.msgbox('成功生成代码，请在当前文件夹下查看', "gps-system")


        if choice == '退出系统':
            # msg = "退出系统吗？"
            # title = "gps-system"
            #
            # # 弹出一个Continue/Cancel对话框
            # if g.ccbox(msg, title, ('继续操作', '退出')):
            #     pass  # 如果继续操作
            # else:
            sys.exit(0)  # 如果退出

        if choice == '开始拟合':
            b_x, b_y, outx, outy, speed_control = Map.out(Map, x, y, flag_x, flag_y, bar_num, model_choose)
            fig1, ax1 = plt.subplots()
            for i in range(len(flag_x)):
                ax1.plot(flag_x[i], flag_y[i], 'bo')
                if i < len(flag_x):
                    ax1.text(flag_x[i] + 0.000005, flag_y[i] + 0.000005, str(i), weight="bold", color="k", fontsize=7)

            ax1.plot(outx, outy, 'ro-')
            ax1.plot(b_x, b_y, 'y-')
            ax1.plot(x[1:3], y[1:3], 'b-')
            for i in range(0, len(speed_control)):
                if speed_control[i] == z_speed:
                    ax1.plot(outx[i], outy[i], 'yo')
                if speed_control[i] == j_speed:
                    ax1.plot(outx[i], outy[i], 'co')

            plt.xlim(min(outx) - 0.00002, max(outx) + 0.00002)
            plt.ylim(min(outy) - 0.00002, max(outy) + 0.00002)

            plt.show()

        if choice == '蓝牙发送':
            outname = g.enterbox("请输入生成文件名：", 'gps-system', 'bt_out1')
            if outname != None:
                bluetooth_out(outx, outy, speed_control,outname + '.txt')
            point_sent('com15', outname + '.txt')
            g.msgbox('发送完毕！')
            break

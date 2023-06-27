# -------------------------------
# GPS_master
# author:恩
# version:2.1
# -------------------------------

# ------------------导入库--------------------
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy import interpolate
import numpy as np
import math
import easygui as g
import sys
import os
from GPS_system import read_point
from GPS_system import make_code
from scipy.special import comb

#-----------------宏定义----------------
stage1 = 110  #阶段1
stage2 = 285
stage3 = 420
stage4 = 470
stage5 = 520
stage6 = 650

z_speed = 12  # 直道速度
s_speed = 6  # s弯速度
y_speed = 6  # 圆环速度

# ----------------------------My_function-----------------------------------------------
def interpolate_points(x, y ,n):
    # 计算参数化曲线的参数 t
    t = np.linspace(0, 1, len(x))

    # 创建插值函数
    tck, u = interpolate.splprep([x, y], s=0)

    # 在曲线上均匀取样n个点
    t_new = np.linspace(0, 1, (len(x)-1)*n+1)
    interpolated_points = interpolate.splev(t_new, tck)

    # 提取插值点的 x 和 y 坐标数组
    interpolated_x = interpolated_points[0]
    interpolated_y = interpolated_points[1]

    return interpolated_x, interpolated_y

def s_bend(x_coords, y_coords, num_points):
    arc_points_x = []
    arc_points_y = []

    for i in range(len(x_coords)-1):
        x1, y1 = x_coords[i], y_coords[i]
        x2, y2 = x_coords[i+1], y_coords[i+1]

        # 计算两点之间的距离和中点坐标
        distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

        # 计算半径和角度增量
        if i == 0:
            radius = distance / 2
        else:
            radius = distance / 1.2

        if i % 2 == 0:  # 上半圆弧
            if i == 0:
                angles = np.linspace(np.pi * 4 / 5 , -np.pi / 2 , num_points+6)
            else:
                angles = np.linspace(np.pi / 4, np.pi / 2, num_points+1)
            circle_points_x = x1 + radius * np.cos(angles)
            circle_points_y = y1 + radius * np.sin(angles)
        else:  # 下半圆弧
            angles = np.linspace(np.pi / 4, np.pi / 2, num_points)
            circle_points_x = x1 - radius * np.cos(angles)
            circle_points_y = y1 - radius * np.sin(angles)

        arc_points_x.extend(circle_points_x)
        arc_points_y.extend(circle_points_y)

    x1, y1 = x_coords[-2], y_coords[-2]
    x2, y2 = x_coords[-1], y_coords[-1]
    distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    radius = distance / 1.2
    if len(x_coords)-1 % 2 == 0:  # 上半圆弧
        angles = np.linspace(np.pi / 4, np.pi / 2, num_points+1)
        circle_points_x = x2 + radius * np.cos(angles)
        circle_points_y = y2 + radius * np.sin(angles)
    else:  # 下半圆弧
        angles = np.linspace(np.pi / 4, np.pi / 2, num_points+1)
        circle_points_x = x2 - radius * np.cos(angles)
        circle_points_y = y2 - radius * np.sin(angles)
    arc_points_x.extend(circle_points_x)
    arc_points_y.extend(circle_points_y)

    return arc_points_x, arc_points_y

def ring(x, y, radius, angle_1, angle_2, num):
    arc_points_x = []
    arc_points_y = []
    angles = np.linspace(angle_1, angle_2, num)
    circle_points_x = x + radius * np.cos(angles)
    circle_points_y = y + radius * np.sin(angles)
    arc_points_x.extend(circle_points_x)
    arc_points_y.extend(circle_points_y)

    return arc_points_x,arc_points_y

def bezier_curve_interpolation(x, y,num):
    n = len(x) - 1  # 控制点数量
    t = np.linspace(0, 1, num)  # 参数化曲线的参数

    curve_x = np.zeros(num)
    curve_y = np.zeros(num)

    for i, t_val in enumerate(t):
        point = np.zeros(2)
        for j in range(n + 1):
            coefficient = comb(n, j) * t_val**j * (1 - t_val)**(n - j)
            point += coefficient * np.array([x[j], y[j]])
        curve_x[i] = point[0]
        curve_y[i] = point[1]

    return curve_x, curve_y

def insert_point(x1, y1, x2, y2, num):
    dx = (x2 - x1 ) / (num + 1)
    dy = (y2 - y1 ) / (num + 1)
    xx = np.linspace(x1 + dx, x2 - dx, num)
    yy = np.linspace(y1 + dy, y2 - dy, num)
    xx = xx.tolist()
    yy = yy.tolist()

    return xx,yy

def make_curve(x, y, flg_x, flg_y, bar_num):
    o_x = []
    o_y = []
    speed = []
    # s弯
    stage2_x, stage2_y = s_bend(flg_x[:bar_num], flag_y[:bar_num], 16)
    # 起点到第一个锥桶
    stage1_x, stage1_y = insert_point(x[0],y[0],stage2_x[0],stage2_y[0], 30)
    #过s弯到掉头区
    stage3_x, stage3_y = insert_point(flg_x[bar_num-1], flg_y[bar_num-1], x[1], y[1], 20)
    #掉头
    stage4_x, stage4_y = ring(x[1], y[1], 1.75e-05, - np.pi / 1.3, np.pi / 4.5, 30)
    #大圆环
    stage6_x, stage6_y = ring(flg_x[bar_num], flg_y[bar_num], 1.36e-05, - np.pi / 4, np.pi * 2.9, 80)
    #掉头点到大圆环
    stage5_x, stage5_y = insert_point(x[1], y[1], stage6_x[0], stage6_y[0], 15)
    #大圆环到终点
    stage7_x, stage7_y = insert_point(stage6_x[-1], stage6_y[-1], x[2], y[2], 50)

    x_list = stage1_x + stage2_x + stage3_x + stage4_x + stage5_x + stage6_x + stage7_x
    y_list = stage1_y + stage2_y + stage3_y + stage4_y + stage5_y + stage6_y + stage7_y
    curve_x, curve_y = bezier_curve_interpolation(x_list,y_list,200) #贝塞尔曲线拟合
    curve_points_x, curve_points_y = interpolate_points(curve_x, curve_y, 5)
    o_x.append(curve_points_x[0])
    o_y.append(curve_points_y[0])
    speed.append(z_speed)
    for i in range(1000):
        ii = i + 1
        if ii <= stage1:  # 直道1
            if ii % 180 == 0:
                o_x.append(curve_points_x[i])
                o_y.append(curve_points_y[i])
                speed.append(z_speed)
        if ii > stage1 and ii <= stage2:  # s弯
            if (ii - 180) % 6 == 0:
                o_x.append(curve_points_x[i])
                o_y.append(curve_points_y[i])
                speed.append(s_speed)
        if ii > stage2 and ii <= stage3:  # 直道2
            if (ii - 510) % 100 == 0:
                o_x.append(curve_points_x[i])
                o_y.append(curve_points_y[i])
                speed.append(z_speed)
        if ii > stage3 and ii <= stage4:  # 掉头
            if (ii - 690) % 6 == 0:
                o_x.append(curve_points_x[i])
                o_y.append(curve_points_y[i])
                speed.append(y_speed)
        if ii > stage4 and ii <= stage5:  # 直道3
            if (ii - 690) % 50 == 0:
                o_x.append(curve_points_x[i])
                o_y.append(curve_points_y[i])
                speed.append(z_speed)
        if ii > stage5 and ii <= stage6:  # 大圆环
            if (ii - 690) % 6 == 0:
                o_x.append(curve_points_x[i])
                o_y.append(curve_points_y[i])
                speed.append(y_speed)
        if ii > stage6 and ii <= len(curve_points_x):  # 直道
            if (ii - 690) % 300 == 0:
                o_x.append(curve_points_x[i])
                o_y.append(curve_points_y[i])
                speed.append(z_speed)

    o_x.append(curve_points_x[-1])
    o_y.append(curve_points_y[-1])
    speed.append(z_speed)

    return curve_points_x,curve_points_y,o_x,o_y,speed


# ----------------------------My_function-----------------------------------------------

if __name__ == "__main__":
    # ------------打开启动文件--------------------
    setname = ''
    while (os.path.exists(setname + '.txt') != True):
        setname = g.enterbox("请输入采取的gps文件：", 'gps-system', 'rec_6')
        if setname == None:
            setname = ''
        else:
            if os.path.exists(setname + '.txt') != True:
                g.msgbox("请确定你的路径下是否有该配置文件！！！", "gps-system")

    # 读点
    x, y, flag_x, flag_y = read_point(setname + ".txt")
    outname = None

    # --------------------------取点完成------------------------------
    bar_num = 4 #锥桶数量
    fig1, ax1 = plt.subplots()
    b_x, b_y, outx, outy ,speed_control= make_curve(x, y, flag_x, flag_y , bar_num)
    for i in range(len(flag_x)):
        ax1.plot(flag_x[i], flag_y[i], 'bo')
        if i < len(flag_x):
            ax1.text(flag_x[i] + 0.000005, flag_y[i] + 0.000005, str(i), weight="bold", color="k", fontsize=7)

    ax1.plot(outx, outy, 'ro')
    ax1.plot(b_x, b_y, 'y-')
    ax1.text(b_x[stage1] + 0.000005, b_y[stage1] + 0.000005, 'stage1', weight="bold", color="r", fontsize=7)
    ax1.text(b_x[stage2] + 0.000005, b_y[stage2] + 0.000005, 'stage2', weight="bold", color="r", fontsize=7)
    ax1.text(b_x[stage3] + 0.000005, b_y[stage3] + 0.000005, 'stage3', weight="bold", color="r", fontsize=7)
    ax1.text(b_x[stage4] + 0.000005, b_y[stage4] + 0.000005, 'stage4', weight="bold", color="r", fontsize=7)
    ax1.text(b_x[stage5] + 0.000005, b_y[stage5] + 0.000005, 'stage5', weight="bold", color="r", fontsize=7)
    ax1.text(b_x[stage6] + 0.000005, b_y[stage6] + 0.000005, 'stage6', weight="bold", color="r", fontsize=7)
    plt.show()
    while True:
        msg = "请选择你的操作"
        title = "gps-system"
        choices = ["开始拟合","输出代码", "退出系统"]
        choice = g.choicebox(msg, title, choices)

        if choice == '输出代码':
            outname = g.enterbox("请输入生成文件名：", 'gps-system', 'out1')
            if outname != None:
                make_code(outx, outy, speed_control,outname + '.txt')
                g.msgbox('成功生成代码，请在当前文件夹下查看', "gps-system")

        if choice == '退出系统':
            msg = "退出系统吗？"
            title = "gps-system"

            # 弹出一个Continue/Cancel对话框
            if g.ccbox(msg, title, ('继续操作', '退出')):
                pass  # 如果继续操作
            else:
                sys.exit(0)  # 如果退出

        if choice == '开始拟合':
            b_x, b_y, outx, outy, speed_control = make_curve(x, y, flag_x, flag_y, bar_num)
            fig1, ax1 = plt.subplots()
            for i in range(len(flag_x)):
                ax1.plot(flag_x[i], flag_y[i], 'bo')
                if i < len(flag_x):
                    ax1.text(flag_x[i] + 0.000005, flag_y[i] + 0.000005, str(i), weight="bold", color="k", fontsize=7)

            ax1.plot(outx, outy, 'ro')
            ax1.plot(b_x, b_y, 'y-')
            ax1.text(b_x[stage1] + 0.000005, b_y[stage1] + 0.000005, 'stage1', weight="bold", color="r", fontsize=7)
            ax1.text(b_x[stage2] + 0.000005, b_y[stage2] + 0.000005, 'stage2', weight="bold", color="r", fontsize=7)
            ax1.text(b_x[stage3] + 0.000005, b_y[stage3] + 0.000005, 'stage3', weight="bold", color="r", fontsize=7)
            ax1.text(b_x[stage4] + 0.000005, b_y[stage4] + 0.000005, 'stage4', weight="bold", color="r", fontsize=7)
            ax1.text(b_x[stage5] + 0.000005, b_y[stage5] + 0.000005, 'stage5', weight="bold", color="r", fontsize=7)
            ax1.text(b_x[stage6] + 0.000005, b_y[stage6] + 0.000005, 'stage6', weight="bold", color="r", fontsize=7)
            plt.show()

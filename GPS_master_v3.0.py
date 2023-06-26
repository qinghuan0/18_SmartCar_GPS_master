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

# ----------------------------My_function-----------------------------------------------
def interpolate_points(x, y ,n):
    # 计算参数化曲线的参数 t
    t = np.linspace(0, 1, len(x))

    # 创建插值函数
    tck, u = interpolate.splprep([x, y], s=0)

    # 在曲线上均匀取样50个点
    t_new = np.linspace(0, 1, (len(x)-1)*n+1)
    interpolated_points = interpolate.splev(t_new, tck)

    # 提取插值点的 x 和 y 坐标数组
    interpolated_x = interpolated_points[0]
    interpolated_y = interpolated_points[1]

    return interpolated_x, interpolated_y

def generate_arc_points(x_coords, y_coords, num_points):
    arc_points_x = []
    arc_points_y = []

    for i in range(len(x_coords)-1):
        x1, y1 = x_coords[i], y_coords[i]
        x2, y2 = x_coords[i+1], y_coords[i+1]

        # 计算两点之间的距离和中点坐标
        distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

        # 计算半径和角度增量
        if i == 0:
            radius = distance / 2.8
        else:
            radius = distance / 1.2

        if i % 2 == 0:  # 上半圆弧
            angles = np.linspace(np.pi / 4, np.pi * 1 / 2, num_points)
            circle_points_x = x1 + radius * np.cos(angles)
            circle_points_y = y1 + radius * np.sin(angles)
        else:  # 下半圆弧
            angles = np.linspace(np.pi / 4, np.pi * 2 / 3, num_points)
            circle_points_x = x1 - radius * np.cos(angles)
            circle_points_y = y1 - radius * np.sin(angles)

        arc_points_x.extend(circle_points_x)
        arc_points_y.extend(circle_points_y)

    x1, y1 = x_coords[-2], y_coords[-2]
    x2, y2 = x_coords[-1], y_coords[-1]
    distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    radius = distance / 1.5
    if len(x_coords)-1 % 2 == 0:  # 上半圆弧
        angles = np.linspace(0, np.pi / 3, num_points)
        circle_points_x = x2 + radius * np.cos(angles)
        circle_points_y = y2 + radius * np.sin(angles)
    else:  # 下半圆弧
        angles = np.linspace(np.pi / 3, np.pi * 2 / 3, num_points)
        circle_points_x = x2 - radius * np.cos(angles)
        circle_points_y = y2 - radius * np.sin(angles)
    arc_points_x.extend(circle_points_x)
    arc_points_y.extend(circle_points_y)

    return arc_points_x, arc_points_y

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
    bar_x = flag_x[:bar_num] #锥桶数组
    bar_y = flag_y[:bar_num]
    # 在起点到第一个锥桶间插入30个点
    stage1_x, stage1_y = insert_point(x[0],y[0],flg_x[0],flg_y[0], 30)
    #过s弯到掉头区插入30个点
    stage2_x, stage2_y = insert_point(flg_x[bar_num-1], flg_y[bar_num-1], x[1], y[1], 30)

    b_x,b_y = generate_arc_points(flg_x[:bar_num],flag_y[:bar_num],10) #锥桶控制点
    x_list = stage1_x + b_x + stage2_x
    y_list = stage1_y + b_y + stage2_y
    lo_x, la_y = bezier_curve_interpolation(x_list,y_list,60) #贝塞尔曲线拟合

    return lo_x,la_y


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
    b_x, b_y = make_curve(x, y, flag_x, flag_y , bar_num)

    for i in range(len(flag_x)):
        ax1.plot(flag_x[i], flag_y[i], 'bo')
        if i < len(flag_x):
            ax1.text(flag_x[i] + 0.000005, flag_y[i] + 0.000005, str(i), weight="bold", color="k", fontsize=7)

    ax1.plot(x, y, 'ro')
    ax1.plot(b_x,b_y,'y-')
    plt.show()

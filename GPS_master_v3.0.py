# -------------------------------
# GPS_master
# author:恩
# version:4.0
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
from GPS_system import Point_Move

#-----------------宏定义----------------
z_speed = 14  # 直道速度
s_speed = 10  # 弯道速度

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

def s_bend(x_coords, y_coords, num_points, flg=0):
    arc_points_x = []
    arc_points_y = []
    last_radius = 0

    for i in range(len(x_coords)-1):
        x1, y1 = x_coords[i], y_coords[i]
        x2, y2 = x_coords[i+1], y_coords[i+1]

        # 计算两点之间的距离和中点坐标
        distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)

        # 计算半径和角度增量
        # if i == 0:
        #     radius = distance / 2
        # else:
        #     radius = distance / 1.2

        radius = ((distance / 1.4)*0.6 + last_radius*1.4) / 2

        if i % 2 == 0:  # 上半圆弧
            if i == 0:
                radius = distance / 1.6
                if x_coords[0] > x_coords[1]:
                    angles = np.linspace(-np.pi / 4, np.pi * 4 / 5, num_points + 6)
                else:
                    angles = np.linspace(np.pi * 4 / 5 , -np.pi / 4 , num_points+6)
            else:
                if flg == 0:
                    radius += last_radius * 0.2
                angles = np.linspace(np.pi / 5, np.pi / 2.4, num_points+1)
            circle_points_x = x1 + radius * np.cos(angles)
            circle_points_y = y1 + radius * np.sin(angles)
        else:  # 下半圆弧
            if flg == 1:
                radius += last_radius * 0.2
                angles = np.linspace(np.pi * 4 / 5 , -np.pi / 4, num_points+2)
            else:
                angles = np.linspace(np.pi / 5, np.pi / 2.2, num_points)
            circle_points_x = x1 - radius * np.cos(angles)
            circle_points_y = y1 - radius * np.sin(angles)

        arc_points_x.extend(circle_points_x)
        arc_points_y.extend(circle_points_y)

        last_radius = radius

    #最后一个
    x1, y1 = x_coords[-2], y_coords[-2]
    x2, y2 = x_coords[-1], y_coords[-1]
    distance = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    radius = distance / 1.4
    if len(x_coords) % 2 != 0:  # 上半圆弧
        angles = np.linspace(np.pi / 5, np.pi / 2.4, num_points+1)
        circle_points_x = x2 + radius * np.cos(angles)
        circle_points_y = y2 + radius * np.sin(angles)
    else:  # 下半圆弧
        if flg == 1:
            angles = np.linspace(np.pi * 4 / 5, -np.pi / 4, num_points)
        else:
            angles = np.linspace(np.pi / 5, np.pi / 2.2, num_points)
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

def calculate_curvature(x, y):
    # 计算曲线上各点的曲率
    dx_dt = np.gradient(x)
    dy_dt = np.gradient(y)
    d2x_dt2 = np.gradient(dx_dt)
    d2y_dt2 = np.gradient(dy_dt)

    curvature = np.abs(d2x_dt2 * dy_dt - dx_dt * d2y_dt2) / (dx_dt ** 2 + dy_dt ** 2) ** 1.5
    return curvature

def filter_points(x, y, threshold):
    # 根据曲率筛选点
    curvature = calculate_curvature(x, y)
    filtered_x = []
    filtered_y = []
    speed = []
    for i in range(len(x)):
        if curvature[i] >= threshold:
            if i % 3 == 0:
                filtered_x.append(x[i])
                filtered_y.append(y[i])
                speed.append(s_speed)
        else:
            if i % 22 == 0:
                filtered_x.append(x[i])
                filtered_y.append(y[i])
                speed.append(z_speed)

    for j in range(1,len(speed)-1):
        if speed[j] == z_speed:
            if speed[j-1] == speed[j+1] == s_speed:
                speed[j] = s_speed
    return filtered_x, filtered_y, speed

def make_curve(x, y, flg_x, flg_y, bar_num):
    # s弯
    stage2_x, stage2_y = s_bend(flg_x[:bar_num], flag_y[:bar_num], 16)
    # 起点到第一个锥桶
    stage1_x, stage1_y = insert_point(x[0],y[0],flg_x[0],flg_y[0], 30)
    del stage1_x[18:]
    del stage1_y[18:]
    #掉头
    if y[1] < flg_y[bar_num-1] and x[1] < flg_x[bar_num-1]:
        stage4_x, stage4_y = ring(x[1], y[1], 0.9e-05,  np.pi / 1.3, - np.pi / 4.5, 30)
    elif y[1] > flg_y[bar_num-1] and x[1] < flg_x[bar_num-1]:
        stage4_x, stage4_y = ring(x[1], y[1], 0.9e-05,  np.pi / 1.3, - np.pi / 4.5, 30)
    elif y[1] < flg_y[bar_num - 1] and x[1] > flg_x[bar_num - 1] and y[0]>y[-1]:
        stage4_x, stage4_y = ring(x[1], y[1], 0.9e-05,  np.pi / 1.3, - np.pi / 4.5, 30)
    elif y[1] < flg_y[bar_num-1] and x[1] > flg_x[bar_num-1] and y[0]<y[-1]:
        stage4_x, stage4_y = ring(x[1], y[1], 0.9e-05, - np.pi / 1.3,  np.pi / 4.5, 30)
    else:
        stage4_x, stage4_y = ring(x[1], y[1], 0.9e-05, - np.pi / 1.3,  np.pi / 4.5, 30)
    #过s弯到掉头区
    stage3_x, stage3_y = insert_point(flg_x[bar_num-1], flg_y[bar_num-1], stage4_x[1], stage4_y[1], 20)
    #大圆环
    if x[1] > flg_x[bar_num]:
        stage6_x, stage6_y = ring(flg_x[bar_num], flg_y[bar_num], 2e-05,  np.pi / 4, - np.pi * 2.9, 80)
    elif x[1] < flg_x[bar_num] and y[0] < flg_y[bar_num]:
        stage6_x, stage6_y = ring(flg_x[bar_num], flg_y[bar_num], 2e-05,  np.pi / 4, - np.pi * 2.9, 80)
    else:
        stage6_x, stage6_y = ring(flg_x[bar_num], flg_y[bar_num], 2e-05, - np.pi / 4, np.pi * 2.9, 80)
    #掉头点到大圆环
    stage5_x, stage5_y = insert_point(x[1], y[1], stage6_x[-6], stage6_y[-6], 15)
    #大圆环到终点
    stage7_x, stage7_y = insert_point(stage6_x[-1], stage6_y[-1], x[2], y[2], 50)

    x_list = stage1_x + stage2_x + stage3_x + stage4_x + stage5_x + stage6_x + stage7_x
    y_list = stage1_y + stage2_y + stage3_y + stage4_y + stage5_y + stage6_y + stage7_y
    curve_x, curve_y = bezier_curve_interpolation(x_list,y_list,200) #贝塞尔曲线拟合
    curve_points_x, curve_points_y = interpolate_points(curve_x, curve_y, 5) #曲线平均插值
    o_x,o_y,speed=filter_points(curve_points_x,curve_points_y,20000) #滤点
    # del o_x[-2:]
    # del o_y[-2:]
    o_x.append(curve_points_x[-1])
    o_y.append(curve_points_y[-1])
    speed.append(z_speed)

    return curve_points_x,curve_points_y,o_x,o_y,speed

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

def s_y__p(x, y, flg_x, flg_y, bar_num): #先过s弯和圆环，掉头过坡道
    # s弯
    stage2_x, stage2_y = s_bend(flg_x[:bar_num], flag_y[:bar_num], 16)
    # 起点到第一个锥桶
    stage1_x, stage1_y = insert_point(x[0],y[0],flg_x[0],flg_y[0], 30)
    del stage1_x[18:]
    del stage1_y[18:]
    #大圆环
    if y[1]<flg_y[bar_num] and flg_x[0]<flg_x[1]: #起点在左上角且向右掉头
        stage3_x, stage3_y = ring(flg_x[bar_num], flg_y[bar_num], 2e-05,  np.pi / 1.5, - np.pi * 2, 80)
    elif y[1]>flg_y[bar_num] and flg_x[0]<flg_x[1]: #起点在左上角且向左掉头
        stage3_x, stage3_y = ring(flg_x[bar_num], flg_y[bar_num], 2e-05, - np.pi * 2, np.pi / 1.5, 80)
    elif y[1]>flg_y[bar_num] and flg_x[0]>flg_x[1]: #起点右下角且向右掉头
        stage3_x, stage3_y = ring(flg_x[bar_num], flg_y[bar_num], 2e-05, np.pi * 1.5, - np.pi * 1.5, 80)
    else:
        stage3_x, stage3_y = ring(flg_x[bar_num], flg_y[bar_num], 2e-05, - np.pi * 2, np.pi / 1.5 , 80)
    #大圆环到掉头区
    stage4_x, stage4_y = insert_point(stage3_x[-1], stage3_y[-1], x[1], y[1], 30)
    #掉头点到坡道
    stage5_x, stage5_y = insert_point(x[1], y[1], 2* x[2]-x[3], 2*y[2]-y[3], 15)
    #坡道
    stage6_x, stage6_y = insert_point(stage5_x[-1], stage5_y[-1], x[3], y[3], 45)
    #坡道到终点
    stage7_x, stage7_y = insert_point(stage6_x[-1], stage6_y[-1], x[-1], y[-1], 50)

    x_list = stage1_x + stage2_x +stage3_x + stage4_x + stage6_x + stage7_x
    y_list = stage1_y + stage2_y +stage3_y + stage4_y + stage6_y + stage7_y
    curve_x, curve_y = bezier_curve_interpolation(x_list,y_list,200) #贝塞尔曲线拟合
    curve_x, curve_y = interpolate_points(curve_x, curve_y, 5) #曲线平均插值
    o_x,o_y,speed=filter_points(curve_x,curve_y,20000) #滤点
    o_x.append(curve_x[-1])
    o_y.append(curve_y[-1])
    speed.append(z_speed)

    return curve_x,curve_y,o_x,o_y,speed

def p__y_s(x, y, flg_x, flg_y, bar_num): #先过坡道，掉头过圆环和s弯
    # 起点到坡道
    stage1_x, stage1_y = insert_point(x[0],y[0],2* x[1]-((x[1]+x[2])/2), 2* y[1]-((y[1]+y[2])/2), 30)
    #坡道
    stage2_x, stage2_y = insert_point(stage1_x[-1], stage1_y[-1], x[2], y[2], 45)
    #坡道到掉头区
    stage3_x, stage3_y = insert_point(stage2_x[-1], stage2_y[-1], x[3], y[3], 30)
    #大圆环
    if x[0]<x[1] and flg_x[0]>flg_x[1]: #起点在左上角且向右掉头
        stage5_x, stage5_y = ring(flg_x[0], flg_y[0], 1.6e-05, np.pi * 1.5, - np.pi , 80)
        # stage5_x, stage5_y = ring(flg_x[0], flg_y[0], 1.6e-05   ,  np.pi / 1.5, - np.pi * 2, 80)
    elif x[0]<x[1] and y[3]<flg_y[0]: #起点在左上角且向左掉头
        stage5_x, stage5_y = ring(flg_x[0], flg_y[0], 1.6e-05, - np.pi * 2, np.pi / 1.5, 80)
    elif x[0]>x[1] and flg_x[0]<flg_x[1]: #起点右下角且向右掉头
        stage5_x, stage5_y = ring(flg_x[0], flg_y[0], 1.6e-05, np.pi * 1.5, - np.pi * 1.5, 80)
    else:
        stage5_x, stage5_y = ring(flg_x[0], flg_y[0], 1.6e-05, - np.pi * 2, np.pi / 2.5 , 80)
    # 掉头点到圆环
    stage4_x, stage4_y = insert_point(stage3_x[-1], stage3_y[-1], stage5_x[0], stage5_y[0], 15)
    # 圆环到s弯
    stage6_x, stage6_y = insert_point(stage5_x[-1],stage5_y[-1],flg_x[len(flg_x)-bar_num],flg_y[len(flg_x)-bar_num], 30)
    del stage1_x[18:]
    del stage1_y[18:]
    # s弯
    stage7_x, stage7_y = s_bend(flg_x[1:], flag_y[1:], 16, 1)
    #s弯到终点
    stage8_x, stage8_y = insert_point(flg_x[-1], flg_y[-1], x[-1], y[-1], 30)
    del stage1_x[18:]
    del stage1_y[18:]

    x_list = stage1_x + stage2_x +stage3_x + stage4_x + stage5_x + stage6_x + stage7_x + stage8_x
    y_list = stage1_y + stage2_y +stage3_y + stage4_y + stage5_y + stage6_y + stage7_y + stage8_y
    curve_x, curve_y = bezier_curve_interpolation(x_list,y_list,200) #贝塞尔曲线拟合
    curve_x, curve_y = interpolate_points(curve_x, curve_y, 5) #曲线平均插值
    o_x,o_y,speed=filter_points(curve_x,curve_y,20000) #滤点
    o_x.append(curve_x[-1])
    o_y.append(curve_y[-1])
    speed.append(z_speed)

    return curve_x,curve_y,o_x,o_y,speed

# ----------------------------My_function-----------------------------------------------

if __name__ == "__main__":
    # ------------打开启动文件--------------------
    setname = ''
    while (os.path.exists(setname + '.txt') != True):
        setname = g.enterbox("请输入采取的gps文件：", 'gps-system', 'p__y_s_left')
        if setname == None:
            setname = ''
        else:
            if os.path.exists(setname + '.txt') != True:
                g.msgbox("请确定你的路径下是否有该配置文件！！！", "gps-system")

    #输入锥桶个数
    bar_num = int(g.enterbox(msg='锥桶个数', title=' ', default='4', strip=True, image=None, root=None))
    # 读点
    x, y, flag_x, flag_y = read_point(setname + ".txt")
    b_x, b_y, outx, outy, speed_control = p__y_s(x, y, flag_x, flag_y, bar_num)
    outname = None

    # --------------------------取点完成------------------------------
    # 这里复制一份留着复位使用
    routx = flag_x.copy()
    routy = flag_y.copy()

    fig1, ax1 = plt.subplots()
    for i in range(len(flag_x)):
        ax1.plot(flag_x[i], flag_y[i], 'bo')
        if i < len(flag_x):
            ax1.text(flag_x[i] + 0.000005, flag_y[i] + 0.000005, str(i), weight="bold", color="k", fontsize=7)

    ax1.plot(outx, outy, 'ro-')
    ax1.plot(b_x, b_y, 'y-')
    plt.show()
    while True:
        msg = "请选择你的操作"
        title = "gps-system"
        choices = ["修改点位","点位复位","开始拟合","输出代码", "退出系统"]
        choice = g.choicebox(msg, title, choices)

        if choice == '修改点位':
            mygps = Point_Move(x, y,flag_x, flag_y)

        if choice == '点位复位':
            x = routx
            y = routy
            routx = flag_x.copy()
            routy = flag_y.copy()
            mygps = Point_Move(flag_x, flag_y, x, y)

        if choice == '输出代码':
            outname = g.enterbox("请输入生成文件名：", 'gps-system', 'out1')
            if outname != None:
                # make_code(outx, outy, speed_control,outname + '.txt')
                make_map(x, y, flag_x, flag_y, outname + '.txt')
                # g.msgbox('成功生成代码，请在当前文件夹下查看', "gps-system")

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

            ax1.plot(outx, outy, 'ro-')
            ax1.plot(b_x, b_y, 'y-')
            plt.show()

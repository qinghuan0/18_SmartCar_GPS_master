# -------------------------------
# GPS_master
# author:恩
# version:4.2
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
z_speed = 18  # 直道速度
s_speed = 10  # 弯道速度
j_speed = 8  # 缓冲速度

# ----------------------------My_function-----------------------------------------------
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


def s_bend(x_list, y_list, amp, num):
    def draw_curve(x1, y1, x2, y2, amplitude, dir, start_flg, end_flg):
        # 计算两点之间的距离和角度
        dx = x2 - x1
        dy = y2 - y1
        distance = np.sqrt(dx ** 2 + dy ** 2) * 2
        angle = np.arctan2(dy, dx)

        # 坐标轴变换
        def transform_x(x, y):
            return x * np.cos(angle) - y * np.sin(angle)

        def transform_y(x, y):
            return x * np.sin(angle) + y * np.cos(angle)

        if dir == 0:
            # 生成 x 坐标点，取周期的前半部分
            if start_flg == 1:
                x = np.linspace(-distance / 4, distance / 2, num)
            elif end_flg == 1:
                x = np.linspace(0, distance * 3 / 4, num)
            else:
                x = np.linspace(0, distance / 2, num)

            # 计算对应的 y 坐标点，使用正弦函数，并根据振幅进行调整
            y = amplitude * np.sin((2 * np.pi / distance) * x)
            new_x = transform_x(x, y) + x1
            new_y = transform_y(x, y) + y1

        else:
            # 生成 x 坐标点，取周期的后半部分
            if start_flg == 1:
                x = np.linspace(-distance / 4, distance / 2, num)
            elif end_flg == 1:
                x = np.linspace(0, distance * 3 / 4, num)
            else:
                x = np.linspace(0, distance / 2, num)

            # 计算对应的 y 坐标点，使用正弦函数，并根据振幅进行调整
            y = - amplitude * np.sin((2 * np.pi / distance) * x)

            # 坐标轴变换
            new_x = transform_x(x, y) + x1
            new_y = transform_y(x, y) + y1
            new_x = np.array(new_x)
            new_y = np.array(new_y)

        return new_x, new_y

    last_x = 0
    last_y = 0

    # 遍历相邻的坐标点，绘制余弦曲线和坐标点
    for i in range(len(x_list) - 2):
        if i % 2 == 0:
            dir = 0
        else:
            dir = 1
        if i == 0:
            start_flg = 1
        else:
            start_flg = 0
        if i == len(x_list) - 3:
            end_flg = 1
        else:
            end_flg = 0
        x_1 = (x_list[i] + x_list[i + 1]) / 2
        y_1 = (y_list[i] + y_list[i + 1]) / 2
        x_2 = (x_list[i + 1] + x_list[i + 2]) / 2
        y_2 = (y_list[i + 1] + y_list[i + 2]) / 2

        # 绘制曲线
        out_x, out_y = draw_curve(x_1, y_1, x_2, y_2, amp, dir, start_flg, end_flg)
        xx = np.hstack((last_x, out_x))
        yy = np.hstack((last_y, out_y))

        last_x = out_x
        last_y = out_y

    xx = xx.tolist()
    yy = yy.tolist()

    return xx, yy

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
    for i in range(len(x)):
        if curvature[i] >= threshold:
            if i % 4 == 0:
                filtered_x.append(x[i])
                filtered_y.append(y[i])

        else:
            # if i < len(x)-1 and curvature[i+1] >= threshold:
            #     filtered_x.append(x[i-2])
            #     filtered_y.append(y[i-2])
            #     filtered_x.append(x[i])
            #     filtered_y.append(y[i])

            if i % 22 == 0:
                filtered_x.append(x[i])
                filtered_y.append(y[i])

    return filtered_x, filtered_y

def speed_planning(x, y):
    speed = []
    value = 1.9e-06
    last_dis = 100
    for i in range(len(x) - 1):
        dis = np.sqrt((x[i+1] - x[i]) ** 2 + (y[i+1] - y[i]) ** 2)
        # print(dis)
        if dis <= value: #距离阈值
            if last_dis > value:
                speed[i - 1] = j_speed #速度缓冲
            speed.append(s_speed)
        else:
            speed.append(z_speed)
        last_dis = dis

    speed.append(z_speed)

    return speed

def s__y_p(x, y, flg_x, flg_y, bar_num): #先过s弯，掉头过圆环和坡道
    # s弯
    stage2_x, stage2_y = s_bend(flg_x[:bar_num], flag_y[:bar_num], 0.00001, 100)
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
    o_x,o_y = filter_points(curve_x,curve_y,35000) #滤点
    # del o_x[-2:]
    # del o_y[-2:]
    o_x.append(curve_points_x[-1])
    o_y.append(curve_points_y[-1])

    speed = speed_planning(o_x, o_y)

    return curve_points_x,curve_points_y,o_x,o_y,speed

def s_y__p(x, y, flg_x, flg_y, bar_num): #先过s弯和圆环，掉头过坡道
    # s弯
    stage2_x, stage2_y = s_bend(flg_x[:bar_num], flag_y[:bar_num], 0.00001, 100)
    # 起点到第一个锥桶
    stage1_x, stage1_y = insert_point(x[0],y[0],stage2_x[0],stage2_y[0], 30)
    del stage1_x[18:]
    del stage1_y[18:]
    #大圆环
    if x[0]<x[1] and y[-1]<y[0]: #起点在左上角且向右掉头
        stage3_x, stage3_y = ring(flg_x[bar_num], flg_y[bar_num], 2e-05,  np.pi / 1.5, - np.pi * 2, 80)
    elif x[0] < x[1] and y[-1] > y[0]:  # 起点在左上角且向左掉头
        stage3_x, stage3_y = ring(flg_x[bar_num], flg_y[bar_num], 2e-05, np.pi / 1.5, - np.pi * 2, 80)
    elif x[0] > x[1] and y[-1] > y[0]:  # 起点右下角且向右掉头
        stage3_x, stage3_y = ring(flg_x[bar_num], flg_y[bar_num], 2e-05, np.pi * 1.5, - np.pi , 80)
    else:
        stage3_x, stage3_y = ring(flg_x[bar_num], flg_y[bar_num], 2e-05, np.pi * 1.5, - np.pi , 80)
    #大圆环到掉头区
    stage4_x, stage4_y = insert_point(stage3_x[-1], stage3_y[-1], x[1], y[1], 30)
    #掉头点到坡道
    stage5_x, stage5_y = insert_point(x[1], y[1], 2* x[2]-x[3], 2*y[2]-y[3], 15)
    #坡道
    stage6_x, stage6_y = insert_point(stage5_x[-1], stage5_y[-1], x[3], y[3], 45)
    #坡道到终点
    stage7_x, stage7_y = insert_point(stage6_x[-1], stage6_y[-1], x[-1], y[-1], 50)

    x_list = stage1_x + stage2_x + stage3_x + stage4_x + stage5_x + stage6_x + stage7_x
    y_list = stage1_y + stage2_y + stage3_y + stage4_y + stage5_y + stage6_y + stage7_y
    curve_x, curve_y = bezier_curve_interpolation(x_list,y_list,200) #贝塞尔曲线拟合
    curve_x, curve_y = interpolate_points(curve_x, curve_y, 5) #曲线平均插值
    o_x,o_y = filter_points(curve_x,curve_y,35000) #滤点
    o_x.append(curve_x[-1])
    o_y.append(curve_y[-1])
    speed = speed_planning(o_x, o_y)

    return curve_x,curve_y,o_x,o_y,speed

def p__y_s(x, y, flg_x, flg_y, bar_num): #先过坡道，掉头过圆环和s弯
    # 起点到坡道
    stage1_x, stage1_y = insert_point(x[0],y[0],2* x[1]-((x[1]+x[2])/2), 2* y[1]-((y[1]+y[2])/2), 15)
    #坡道
    stage2_x, stage2_y = insert_point(stage1_x[-1], stage1_y[-1], 2 * x[2] - x[1], 2 * y[2] - y[1], 150)
    #坡道到掉头区
    stage3_x, stage3_y = insert_point(stage2_x[-1], stage2_y[-1], x[3], y[3], 10)
    #大圆环
    if x[0]<x[1] and y[-1]<y[0]: #起点在左上角且向右掉头
        stage5_x, stage5_y = ring(flg_x[0], flg_y[0], 2.8e-05, np.pi * 1.5, - np.pi * 0.8 , 80)
    elif x[0]<x[1] and y[-1]>y[0]: #起点在左上角且向左掉头
        stage5_x, stage5_y = ring(flg_x[0], flg_y[0], 2.8e-05, - np.pi * 2, np.pi / 2.5 , 80)
    elif x[0]>x[1] and y[-1]>y[0]: #起点右下角且向右掉头
        stage5_x, stage5_y = ring(flg_x[0], flg_y[0], 2.8e-05, np.pi * 1.5, - np.pi * 1.5, 80)
    else:
        stage5_x, stage5_y = ring(flg_x[0], flg_y[0], 2.8e-05, - np.pi , np.pi * 1.3 , 80)
    # 掉头点到圆环
    stage4_x, stage4_y = insert_point(stage3_x[-1], stage3_y[-1], stage5_x[0], stage5_y[0], 15)
    # s弯
    if x[0] < x[1]:
        stage7_x, stage7_y = s_bend(flg_x[1:], flag_y[1:], 0.00001, 100)
    else:
        stage7_x, stage7_y = s_bend(flg_x[1:], flag_y[1:], 0.00001, 100)
    # 圆环到s弯
    stage6_x, stage6_y = insert_point(stage5_x[-1],stage5_y[-1],stage7_x[0],stage7_y[0], 30)
    #s弯到终点
    stage8_x, stage8_y = insert_point(stage7_x[-1],stage7_y[-1], x[-1], y[-1], 30)

    x_list = stage1_x + stage2_x +stage3_x + stage4_x + stage5_x + stage6_x + stage7_x + stage8_x
    y_list = stage1_y + stage2_y +stage3_y + stage4_y + stage5_y + stage6_y + stage7_y + stage8_y
    curve_x, curve_y = bezier_curve_interpolation(x_list,y_list,200) #贝塞尔曲线拟合
    curve_x, curve_y = interpolate_points(curve_x, curve_y, 5) #曲线平均插值
    o_x,o_y = filter_points(curve_x,curve_y,35000) #滤点
    o_x.append(curve_x[-1])
    o_y.append(curve_y[-1])
    speed = speed_planning(o_x, o_y)

    return curve_x,curve_y,o_x,o_y,speed

def model(x, y, flag_x, flag_y, bar_num,model):
    if model == '坡道--圆环_s弯':
        bx, by, ox, oy, speed = p__y_s(x, y, flag_x, flag_y, bar_num)
    elif model == 's弯--圆环_坡道':
        bx, by, ox, oy, speed = s__y_p(x, y, flag_x, flag_y, bar_num)
    else:
        bx, by, ox, oy, speed = s_y__p(x, y, flag_x, flag_y, bar_num)

    return bx, by, ox, oy, speed

# ----------------------------My_function-----------------------------------------------

if __name__ == "__main__":
    # ------------打开启动文件--------------------
    setname = ''
    while (os.path.exists(setname + '.txt') != True):
        setname = g.enterbox("请输入采取的gps文件：", 'gps-system', 'p__y_s_right')
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
    b_x, b_y, outx, outy, speed_control = model(x, y, flag_x, flag_y, bar_num, model_choose)
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
    ax1.plot(x[1:3], y[1:3], 'b-')
    for i in range(0,len(speed_control)):
        if speed_control[i] == z_speed:
            ax1.plot(outx[i],outy[i], 'yo')
        if speed_control[i] == j_speed:
            ax1.plot(outx[i], outy[i], 'co')

    plt.show()
    while True:
        msg = "请选择你的操作"
        title = "gps-system"
        choices = ["修改点位","点位复位","开始拟合","输出代码", "输出地图", "退出系统"]
        choice = g.choicebox(msg, title, choices)

        if choice == '修改点位':
            mygps = Point_Move(flag_x, flag_y, x, y)

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
            b_x, b_y, outx, outy, speed_control = model(x, y, flag_x, flag_y, bar_num, model_choose)
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
            plt.show()


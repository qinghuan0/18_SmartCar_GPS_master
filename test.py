import numpy as np
import matplotlib.pyplot as plt
from GPS_system import read_point
from scipy import interpolate
from GPS_system import make_code
from scipy.special import comb
from GPS_system import Point_Move

z_speed = 18  # 直道速度
s_speed = 10  # 弯道速度
j_speed = 8  # 缓冲速度

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
                speed[i - 1] = j_speed
            speed.append(s_speed)
        else:
            speed.append(z_speed)
        last_dis = dis

    speed.append(z_speed)

    return speed

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
        stage3_x, stage3_y = ring(flg_x[bar_num], flg_y[bar_num], 2e-05, - np.pi * 2, np.pi / 1.5, 80)
    elif x[0] > x[1] and y[-1] > y[0]:  # 起点右下角且向右掉头
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

    x_list = stage1_x + stage2_x + stage3_x + stage4_x + stage5_x + stage6_x + stage7_x
    y_list = stage1_y + stage2_y + stage3_y + stage4_y + stage5_y + stage6_y + stage7_y
    curve_x, curve_y = bezier_curve_interpolation(x_list,y_list,200) #贝塞尔曲线拟合
    curve_x, curve_y = interpolate_points(curve_x, curve_y, 5) #曲线平均插值
    o_x,o_y = filter_points(curve_x,curve_y,35000) #滤点
    o_x.append(curve_x[-1])
    o_y.append(curve_y[-1])
    speed = speed_planning(o_x, o_y)

    return curve_x,curve_y,o_x,o_y,speed

if __name__ == "__main__":
    setname = 's-y--p-left'
    bar_num = 4
    x, y, flag_x, flag_y = read_point(setname + ".txt")
    b_x, b_y, outx, outy, speed_control = s_y__p(x, y, flag_x, flag_y, bar_num)
    outname = None

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

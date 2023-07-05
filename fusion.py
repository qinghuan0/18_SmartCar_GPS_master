# -------------------------------
# fusion.py
# author:恩
# version:4.2
# -------------------------------

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy import interpolate
import numpy as np
from scipy.special import comb
z_speed = 18  # 直道速度
s_speed = 10  # 弯道速度
j_speed = 8  # 缓冲速度

# ----------------------------My_function-----------------------------------------------
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

# ----------------动态图的类------------------------
class Point_Move:
    showverts = True
    offset = 0.00001  # 距离偏差设置

    def __init__(self,ox, oy, flg_x, flg_y):
        # 创建figure（绘制面板）、创建图表（axes）
        self.fig, self.ax = plt.subplots()
        # 设置标题
        self.ax.set_title('Click and drag a point to move it')
        # 设置坐标轴范围
        self.ax.set_xlim((min(ox) - 0.00005, max(ox) + 0.00005))
        self.ax.set_ylim((min(oy) - 0.00005, max(oy) + 0.00005))
        self.ax.plot(ox, oy, '-y')
        self.ax.plot(flg_x,flg_y,'bo')
        self.x = ox
        self.y = oy
        # 绘制2D的动画line
        self.line = Line2D(self.x, self.y, linewidth=1, ls="--",
                           marker='o', markerfacecolor='r',
                           animated=True)
        self.ax.add_line(self.line)
        # 标志值设为none
        self._ind = None
        # 设置画布，方便后续画布响应事件
        canvas = self.fig.canvas
        canvas.mpl_connect('draw_event', self.draw_callback)
        canvas.mpl_connect('button_press_event', self.button_press_callback)
        canvas.mpl_connect('button_release_event', self.button_release_callback)
        canvas.mpl_connect('motion_notify_event', self.motion_notify_callback)
        self.canvas = canvas
        plt.grid()
        for i in range(len(self.x)):
            plt.text(self.x[i] + 0.000005, self.y[i] + 0.000005, str(i), weight="bold", color="k", fontsize=7)
        plt.show()

    ''
    ''
    ' -------------------动作一:界面重新绘制------------------------------- '

    # 界面重新绘制:draw_event
    def draw_callback(self, event):
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)

    ''
    ''

    # -------------------函数:识别按下的点----------------------------------
    def get_ind_under_point(self, event):
        'get the index of the vertex under point if within epsilon tolerance'
        # 在公差允许的范围内，求出鼠标点下顶点坐标的数值
        # x1,y1 and x2,y2对应当前点坐标
        xt, yt = np.array(self.x), np.array(self.y)  # xt = [x1 , x2 ]    yt  =  [y1   ,  y2]
        d = np.sqrt((xt - event.xdata) ** 2 + (yt - event.ydata) ** 2)  # 计算鼠标对应点到该点的距离
        indseq = np.nonzero(np.equal(d, np.amin(d)))[0]  # 找到按下的点并计算点对应的索引
        ind = indseq[0]  # 把对应点的索引拿出来
        # 如果在公差范围内，则返回ind的值
        if d[ind] >= self.offset:
            ind = None
        return ind

    ''
    ''

    # ---------------动作二：鼠标被按下-----------------------------
    # ---------------鼠标被按下，立即计算最近的顶点下标----------------------
    def button_press_callback(self, event):
        'whenever a mouse button is pressed'

        # --------不做处理的情况-----------
        if not self.showverts: return
        if event.inaxes == None: return
        if event.button != 1: return
        # --------不做处理的情况-----------

        # 把参数传进对象
        self._ind = self.get_ind_under_point(event)

    ''
    ''

    # -----------------------动作三:鼠标被释放---------------------------
    # ------------------鼠标释放后，清空、重置------------------------
    def button_release_callback(self, event):
        'whenever a mouse button is released'
        # --------不做处理的情况-----------
        if not self.showverts: return
        if event.button != 1: return
        # --------不做处理的情况-----------
        self._ind = None  # ind恢复None

    ''
    ''

    # -------------------动作四:鼠标移动----------------------------
    # ----------------鼠标移动的事件-------------------
    def motion_notify_callback(self, event):
        'on mouse movement'
        # --------不做处理的情况-----------
        if not self.showverts: return
        if self._ind is None: return
        if event.inaxes is None: return
        if event.button != 1: return
        # --------不做处理的情况-----------
        # 更新数据
        x, y = event.xdata, event.ydata
        self.x[self._ind] = x
        self.y[self._ind] = y
        # 根据更新的数值，重新绘制图形
        self.line = Line2D(self.x, self.y, linewidth=1, ls="--",
                           marker='o', markerfacecolor='r',
                           animated=True)
        self.ax.add_line(self.line)
        # 恢复背景
        self.canvas.restore_region(self.background)
        self.ax.draw_artist(self.line)
        self.canvas.blit(self.ax.bbox)

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

# ----------------------------My_function-----------------------------------------------
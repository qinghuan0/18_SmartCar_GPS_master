# -------------------------------
# GPS system
# author:恩
# version:1

# -------------------------------


# ------------------导入库--------------------
import serial
import folium
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.artist import Artist
from matplotlib.patches import Polygon
from scipy import interpolate
import numpy as np
import math
import easygui as g
import sys
import os
import keyboard
import struct


# ----------------------------My_function-----------------------------------------------

# ---------------串口接收函数-------------------------
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

# ---------------生成程序函数-------------------------
def make_code(x, y, your_name):
    # -----------save---txt--------------
    # 输出限制在小数点后6位
    for i in range(len(x)):
        x[i] = round(x[i], 6)
        y[i] = round(y[i], 6)

    n = len(x)
    mystr = ''
    for i in range(n):
        mystr = mystr + 'targget' + '[' + str(i) + ']' + '[0]'
        mystr = mystr + '=' + str(y[i]) + ','
        mystr = mystr + 'targget' + '[' + str(i) + ']' + '[1]'
        mystr = mystr + '=' + str(x[i]) + ';' + '\n'
    # print(mystr)
    # 看是否需要加点
    # for i in range(4):
    #     mystr = mystr + 'targget' + '[' + str(i+n) + ']' + '[0]'
    #     mystr = mystr + '=' + str(y[i]) + ','
    #     mystr = mystr + 'targget' + '[' + str(i+n) + ']' + '[1]'
    #     mystr = mystr + '=' + str(x[i]) + ';' + '\n'
    with open(your_name, "w") as g:
        g.write(mystr)


# ---------------经纬度转平面坐标系（LLA--->NEU）------------------------
def gps_LLAtoNEU(a, b, sa, sb):
    longitude = a
    latitude = b
    start_longitude = sa
    start_latitude = sb
    c = []
    d = []
    n = len(a)
    earth = 6378137  # 地球半径，单位：m
    pi = 3.1415926535898
    for i in range(n):
        now_longitude = longitude[i]
        now_latitude = latitude[i]
        rad_latitude1 = start_latitude * pi / 180
        rad_latitude2 = now_latitude * pi / 180
        rad_longitude1 = start_longitude * pi / 180
        rad_longitude2 = now_longitude * pi / 180
        aaa = rad_latitude1 - rad_latitude2
        bbb = rad_longitude1 - rad_longitude2
        distance = 2 * math.asin(math.sqrt(pow(math.sin(aaa / 2), 2) + math.cos(rad_latitude1)
                                           * math.cos(rad_latitude2) * pow(math.sin(bbb / 2), 2)))
        distance = distance * earth
        ccc = math.sin(rad_longitude2 - rad_longitude1) * math.cos(rad_latitude2)
        ddd = math.cos(rad_latitude1) * math.sin(rad_latitude2) - math.sin(rad_latitude1) \
              * math.cos(rad_latitude2) * math.cos(rad_longitude2 - rad_longitude1)
        angle = math.atan2(ccc, ddd) * 180 / pi
        if angle < 0:
            angle = angle + 360
        angle2 = (450 - angle) * pi / 180
        px = distance * math.cos(angle2)
        py = distance * math.sin(angle2)
        c.append(px)
        d.append(py)

    return c, d


# --------------------拟合曲线函数----------------------------
def make_curve(control_points_x, control_points_y,num_points):#贝塞尔曲线拟合
    n = len(control_points_x) - 1
    t = np.linspace(0, 1, num_points)
    curve_points_x = np.zeros(num_points)
    curve_points_y = np.zeros(num_points)

    for i in range(num_points):
        point_x = 0.0
        point_y = 0.0
        for j in range(n + 1):
            coefficient = np.math.comb(n, j) * t[i] ** j * (1 - t[i]) ** (n - j)
            point_x += coefficient * control_points_x[j]
            point_y += coefficient * control_points_y[j]
        curve_points_x[i] = point_x
        curve_points_y[i] = point_y

    return curve_points_x, curve_points_y

# ----------------动态图的类------------------------
class Point_Move:
    showverts = True
    offset = 0.00001  # 距离偏差设置

    def __init__(self,ox, oy):
        # 创建figure（绘制面板）、创建图表（axes）
        self.fig, self.ax = plt.subplots()
        # 设置标题
        self.ax.set_title('Click and drag a point to move it')
        self.ax.plot(ox, oy, '-y')
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
        print(self._ind)

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


# 按NEU坐标系显示
def myplot_NEU(outx, outy, xi, yi):
    neux, neuy = gps_LLAtoNEU(outx, outy, outx[0], outy[0])
    neuxi, neuyi = gps_LLAtoNEU(xi, yi, outx[0], outy[0])

    fig2, ax2 = plt.subplots()
    for i in range(len(neux)):
        ii = i + 1
        ax2.plot(neux[i], neuy[i], 'or')
        if i < len(neux):
            ax2.text(neux[i] + 0.000005, neuy[i] + 0.000005, str(i), weight="bold", color="k", fontsize=7)

    ax2.plot(neuxi, neuyi, '-y')
    ax2.plot(neux, neuy, '--r')
    plt.show()

#计算曲率
def compute_curvature(x, y):
    # 将 x 和 y 转换为 NumPy 数组
    x = np.array(x)
    y = np.array(y)

    # 计算一阶导数（速度向量）
    dx = np.gradient(x)
    dy = np.gradient(y)

    # 计算二阶导数（加速度向量）
    d2x = np.gradient(dx)
    d2y = np.gradient(dy)

    # 计算速度向量的模长（即速度的大小）：
    magnitude = np.sqrt(dx**2 + dy**2)

    # 计算曲率：
    curvature = (d2x * dy - dx * d2y) / magnitude**3

    return curvature

#速度规划
def speed_control(x,y):
    value = -9.97137583e+02 #曲率的阈值，可以观察打印出来的曲率数组修改
    velocity = np.array([])
    curvature = compute_curvature(x,y)
    print("曲率数组为:", curvature)
    n = len(curvature)
    keep = np.ones(len(x), dtype=bool)
    keep_s = np.ones(len(x), dtype=bool)
    keep_s[0] = True
    for i in range(n):
        point_curvature = curvature[i]
        if point_curvature < value and 0 <i< n-2 : #根据曲率滤掉一些直道的点
            straight_flag = 1
            keep[i] = False
            if i != n-1 and i>0:
                keep_s[i-1] = False
        elif i<=1 or i>=n-1:
            straight_flag = 1
        else:
            straight_flag = 0

        if straight_flag == 1:
            velocity = np.append(velocity,7)  # 直道速度
        else:
            velocity = np.append(velocity,5)  # 弯道速度


    return keep #返回过滤后的点位数组和速度数组


# ----------------------------My_function-----------------------------------------------


if __name__ == "__main__":

    # ---------------欢迎界面----------------
    g.msgbox("----------------------------极速越野组gps调试系统----------------------------\n"
             'gps-system','CHDlogo.jpg','启动' )

    # ------------打开启动文件--------------------
    ser = serial.Serial('COM15', 115200, timeout=0)  # 修改端口号和波特率

    x,y = gps_receive()
    point_num = 100

    # GPS_list=[[110.29784393310547, 21.153764724731445], [110.29788970947266, 21.15373992919922],
    #          [110.29791259765625, 21.15373992919922], [110.29792022705078, 21.153743743896484],
    #          [110.29793548583984, 21.15374755859375], [110.29793548583984, 21.15373420715332],
    #          [110.29793548583984, 21.15372085571289], [110.29793548583984, 21.153705596923828],
    #          [110.2979507446289, 21.15370750427246], [110.29796600341797, 21.15372085571289],
    #          [110.2979736328125, 21.153722763061523], [110.29798126220703, 21.153718948364258],
    #          [110.29798126220703, 21.15370750427246], [110.2979965209961, 21.153696060180664],
    #          [110.29801177978516, 21.153701782226562], [110.29801177978516, 21.153715133666992],
    #          [110.29785919189453, 21.153789520263672]]
    #
    # x = []
    # y = []

    # for i in range(0,len(GPS_list)):
    #     # x_gps = round(GPS_list[i][0],6)
    #     # y_gps = round(GPS_list[i][1],6)
    #     # x.append(x_gps)
    #     # y.append(y_gps)
    #     x.append(GPS_list[i][0])
    #     y.append(GPS_list[i][1])

    print("x=", x)
    print("y=", y)

    xi, yi = make_curve(x, y,point_num)

    outname = None

    # ------------------先拟合一次-------------------------------
    bool_keep = speed_control(xi, yi)
    xi_np = np.array(xi[bool_keep])
    yi_np = np.array(yi[bool_keep])
    outx = xi_np.tolist()
    outy = yi_np.tolist()


    # NEU坐标系下查看
    # myplot_NEU(outx, outy, xi, yi)

    # --------------------------取点完成------------------------------

    # 这里复制一份留着复位使用
    routx = x.copy()
    routy = y.copy()

    # 调用可调plot类
    mygps = Point_Move(xi, yi)
    finalx = mygps.x
    finaly = mygps.y
    # print("finalx=",finalx)
    # print("finaly=",finaly)

    while True:
        msg = "请选择你的操作"
        title = "gps-system"
        choices = ["显示原始点位", "继续调整轨迹", "轨迹复位", "开始拟合","NEU坐标系下查看点","输出代码", "退出系统"]
        choice = g.choicebox(msg, title, choices)

        if choice == '显示原始点位':
            fig1, ax1 = plt.subplots()
            for i in range(len(x)):
                ax1.plot(x[i], y[i], 'or')
                if i < len(outx):
                    ax1.text(x[i] + 0.000005, y[i] + 0.000005, str(i), weight="bold", color="k", fontsize=7)

            ax1.plot(x,y, '--r')
            plt.show()

        if choice == '继续调整轨迹':
            # g.msgbox("你的选择是: " + str(choice), "gps-system")
            mygps.__init__(x, y)

        if choice == '轨迹复位':
            # g.msgbox("你的选择是: " + str(choice), "gps-system")
            x = routx
            y = routy
            mygps.__init__(x, y)

        if choice == '输出代码':
            # g.msgbox("你的选择是: " + str(choice), "gps-system")
            outname = g.enterbox("请输入生成文件名：", 'gps-system', 'out1')
            if outname != None:
                make_code(finalx, finaly, outname + '.txt')
                g.msgbox('成功生成代码，请在当前文件夹下查看', "gps-system")

        if choice == '退出系统':
            msg = "退出系统吗？"
            title = "gps-system"

            # 弹出一个Continue/Cancel对话框
            if g.ccbox(msg, title, ('继续操作', '退出')):
                pass  # 如果继续操作
            else:
                sys.exit(0)  # 如果退出

        if choice == 'NEU坐标系下查看点':
            myplot_NEU(outx, outy, xi, yi)

        if choice == '开始拟合':
            xi, yi = make_curve(x, y, point_num)

            bool_keep = speed_control(xi, yi)
            xi_np = np.array(xi[bool_keep])
            yi_np = np.array(yi[bool_keep])
            outx = xi_np.tolist()
            outy = yi_np.tolist()

            # print(outx)
            # print(outy)

            # 修改前自己先查看一下点的分布情况，不行直接停止程序再改
            fig1, ax1 = plt.subplots()
            for i in range(len(outx)):
                ax1.plot(outx[i], outy[i], 'or')
                if i < len(outx):
                    ax1.text(outx[i] + 0.000005, outy[i] + 0.000005, str(i), weight="bold", color="k", fontsize=7)

            ax1.plot(xi, yi, '-y')
            ax1.plot(outx, outy, '--r')
            plt.show()



# -------------------------------
# GPS_system
# author:恩
# version:2.1
# -------------------------------


# ------------------导入库--------------------
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

#-----------------宏定义----------------
stage1 = 100  #阶段一
stage2 = 400
stage3 = 410
stage4 = 700

# ----------------------------My_function-----------------------------------------------

# ---------------读取函数----------------------
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
        file.write("\n*********************lo***********************\n")
        for i in range(0, n):
            x[i] = round(x[i],6)
            file.write(str(x[i]) + ',')
            if i % 5 == 0 and i != 0:
                file.write("\n")
        file.write("\n*********************la***********************\n")
        for i in range(0, n):
            y[i] = round(y[i], 6)
            file.write(str(y[i]) + ',')
            if i % 5 == 0 and i != 0:
                file.write("\n")
        file.write("\n******************velocity*********************\n")
        for i in range(0, n):
            file.write(str(speed[i]) + ',')
            if i % 5 == 0 and i != 0:
                file.write("\n")

# --------------------拟合曲线函数----------------------------
def make_curve(control_points_x, control_points_y):

    # list转numpy
    use_x = np.array(control_points_x)
    use_y = np.array(control_points_y)

    # 去掉重复的点
    okay = np.where(np.abs(np.diff(use_x)) + np.abs(np.diff(use_y)) > 0)
    use_xx = np.r_[use_x[okay],use_x[-1]]
    use_yy = np.r_[use_y[okay],use_y[-1]]

    tck, u = interpolate.splprep([use_xx, use_yy], s=0)
    # evaluate the spline fits for 1000 evenly spaced distance values
    curve_points_x, curve_points_y = interpolate.splev(np.linspace(0, 1, 1000), tck)

    # n = len(control_points_x) - 1
    # t = np.linspace(0, 1, 1000)
    # curve_points_x = np.zeros(1000)
    # curve_points_y = np.zeros(1000)
    o_x = []
    o_y = []
    o_x.append(x[0])
    o_y.append(y[0])

    speed = [] #速度数组
    z_speed = 12 #直道速度
    s_speed = 6 #s弯速度
    y_speed = 6 #圆环速度
    speed.append(z_speed)

    for i in range(1000):
        ii = i + 1

        #贝塞尔曲线拟合
        # point_x = 0.0
        # point_y = 0.0
        # for j in range(n + 1):
        #     coefficient = np.math.comb(n, j) * t[i] ** j * (1 - t[i]) ** (n - j)
        #     point_x += coefficient * control_points_x[j]
        #     point_y += coefficient * control_points_y[j]
        # curve_points_x[i] = point_x
        # curve_points_y[i] = point_y

        if ii <= stage1:  # 直道
            if ii % 180 == 0:
                o_x.append(curve_points_x[i])
                o_y.append(curve_points_y[i])
                speed.append(z_speed)
        if ii > stage1 and ii <= stage2:  # s弯
            if (ii - 180) % 16 == 0:
                o_x.append(curve_points_x[i])
                o_y.append(curve_points_y[i])
                speed.append(s_speed)
        if ii > stage2 and ii <= stage3:  # 直道
            if (ii - 510) % 50 == 0:
                o_x.append(curve_points_x[i])
                o_y.append(curve_points_y[i])
                speed.append(z_speed)
        if ii > stage3 and ii <= stage4:  # 大圆环
            if (ii - 690) % 16 == 0:
                o_x.append(curve_points_x[i])
                o_y.append(curve_points_y[i])
                speed.append(y_speed)
        if ii > stage4 and ii <= 1000:  # 直道
            if (ii - 690) % 300 == 0:
                o_x.append(curve_points_x[i])
                o_y.append(curve_points_y[i])
                speed.append(z_speed)

    return curve_points_x, curve_points_y, o_x, o_y, speed

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

# ----------------------------My_function-----------------------------------------------


if __name__ == "__main__":

    # ---------------欢迎界面----------------
    # g.msgbox("-----------------------------越野组gps调试系统----------------------------\n"
    #          "-------------------------------version:2.1---------------------------------",
    #          'gps-system',
    #          '启动', 'en_logo.jpg')

    # ------------打开启动文件--------------------
    setname = ''
    while (os.path.exists(setname + '.txt') != True):
        setname = g.enterbox("请输入采取的gps文件：", 'gps-system', 'rec_1')
        if setname == None:
            setname = ''
        else:
            if os.path.exists(setname + '.txt') != True:
                g.msgbox("请确定你的路径下是否有该配置文件！！！", "gps-system")

    # 读点
    x, y, flag_x, flag_y = read_point(setname + ".txt")

    xi, yi, outx, outy, speed_control = make_curve(x, y)
    outname = None

    # --------------------------取点完成------------------------------

    # 这里复制一份留着复位使用
    routx = x.copy()
    routy = y.copy()

    # 调用可调plot类
    mygps = Point_Move(x,y,flag_x,flag_y)
    while True:
        msg = "请选择你的操作"
        title = "gps-system"
        choices = ["调整轨迹", "轨迹复位", "开始拟合","输出代码", "退出系统"]
        choice = g.choicebox(msg, title, choices)

        if choice == '调整轨迹':
            mygps.__init__(x, y, flag_x, flag_y)

        if choice == '轨迹复位':
            x = routx
            y = routy
            routx = x.copy()
            routy = y.copy()
            mygps.__init__(x, y, flag_x, flag_y)

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
            xi, yi, outx, outy, speed_control = make_curve(x, y)

            fig1, ax1 = plt.subplots()
            for i in range(len(outx)):
                ax1.plot(outx[i], outy[i], 'or')
                if i < len(outx):
                    ax1.text(outx[i] + 0.000005, outy[i] + 0.000005, str(i), weight="bold", color="k", fontsize=7)

            ax1.plot(xi, yi, '-y')
            ax1.plot(outx, outy, '--r')
            ax1.plot(flag_x, flag_y, 'bo')
            ax1.text(xi[stage1] + 0.000005 ,yi[stage1] + 0.000005,'stage1',weight="bold",color="r",fontsize=7)
            ax1.text(xi[stage2] + 0.000005, yi[stage2] + 0.000005, 'stage2', weight="bold", color="r", fontsize=7)
            ax1.text(xi[stage3] + 0.000005, yi[stage3] + 0.000005, 'stage3', weight="bold", color="r", fontsize=7)
            ax1.text(xi[stage4] + 0.000005, yi[stage4] + 0.000005, 'stage4', weight="bold", color="r", fontsize=7)
            plt.show()


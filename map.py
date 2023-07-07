# -------------------------------
# map.py
# author:恩
# version:4.2
# -------------------------------
from fusion import *

class Map:
    def out(self, x, y, flag_x, flag_y, bar_num, model):
        if model == '坡道--圆环_s弯':
            bx, by, ox, oy, speed = self.p__y_s(self, x, y, flag_x, flag_y, bar_num)
        elif model == 's弯--圆环_坡道':
            bx, by, ox, oy, speed = self.s__y_p(self, x, y, flag_x, flag_y, bar_num)
        else:
            bx, by, ox, oy, speed = self.s_y__p(self, x, y, flag_x, flag_y, bar_num)

        return bx, by, ox, oy, speed

    def s__y_p(self, x, y, flg_x, flg_y, bar_num): #先过s弯，掉头过圆环和坡道
        # s弯
        stage2_x, stage2_y = s_bend(flg_x[:bar_num], flg_y[:bar_num], 0.00001, 100)
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
        for i in range(5): #终点加点避免蓝牙末尾丢包导致丢点
            o_x.append(curve_x[-1])
            o_y.append(curve_y[-1])

        speed = speed_planning(o_x, o_y)

        return curve_points_x,curve_points_y,o_x,o_y,speed

    def s_y__p(self, x, y, flg_x, flg_y, bar_num): #先过s弯和圆环，掉头过坡道
        if bar_num %2 == 0:
            turn = 0
        else:
            turn = 1
        # s弯
        if (x[0] > x[1] and y[-1] < y[0]) or (x[0] < x[1] and y[-1] > y[0]):
            stage2_x, stage2_y = s_bend(flg_x[:bar_num], flg_y[:bar_num], 0.00001, 100, abs(turn - 1))
        else:
            stage2_x, stage2_y = s_bend(flg_x[:bar_num], flg_y[:bar_num], 0.00001, 100, turn)
        del stage2_x[0]
        del stage2_y[0]
        # 起点到第一个锥桶
        stage1_x, stage1_y = insert_point(x[0],y[0],stage2_x[0],stage2_y[0], 30)
        del stage1_x[18:]
        del stage1_y[18:]
        #大圆环
        if x[0]<x[1] and y[-1]<y[0]: #起点在左上角且向右掉头
            stage3_x, stage3_y = ring(flg_x[bar_num], flg_y[bar_num], 2e-05,  np.pi / 1.5, - np.pi * 2, 80)
        elif x[0] < x[1] and y[-1] > y[0]:  # 起点在左上角且向左掉头
            stage3_x, stage3_y = ring(flg_x[bar_num], flg_y[bar_num], 2e-05, - np.pi , np.pi * 1.5, 80)
        elif x[0] > x[1] and y[-1] > y[0]:  # 起点右下角且向右掉头
            stage3_x, stage3_y = ring(flg_x[bar_num], flg_y[bar_num], 2e-05, np.pi * 1.5, - np.pi , 80)
        else:
            stage3_x, stage3_y = ring(flg_x[bar_num], flg_y[bar_num], 2e-05, 0 , np.pi * 2.5 , 80)
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
        for i in range(5): #终点加点避免蓝牙末尾丢包导致丢点
            o_x.append(curve_x[-1])
            o_y.append(curve_y[-1])
        speed = speed_planning(o_x, o_y)

        return curve_x,curve_y,o_x,o_y,speed

    def p__y_s(self, x, y, flg_x, flg_y, bar_num): #先过坡道，掉头过圆环和s弯
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
            stage7_x, stage7_y = s_bend(flg_x[1:], flg_y[1:], 0.00001, 100)
        else:
            stage7_x, stage7_y = s_bend(flg_x[1:], flg_y[1:], 0.00001, 100)
        # 圆环到s弯
        stage6_x, stage6_y = insert_point(stage5_x[-1],stage5_y[-1],stage7_x[0],stage7_y[0], 30)
        #s弯到终点
        stage8_x, stage8_y = insert_point(stage7_x[-1],stage7_y[-1], x[-1], y[-1], 30)

        x_list = stage1_x + stage2_x +stage3_x + stage4_x + stage5_x + stage6_x + stage7_x + stage8_x
        y_list = stage1_y + stage2_y +stage3_y + stage4_y + stage5_y + stage6_y + stage7_y + stage8_y
        curve_x, curve_y = bezier_curve_interpolation(x_list,y_list,200) #贝塞尔曲线拟合
        curve_x, curve_y = interpolate_points(curve_x, curve_y, 5) #曲线平均插值
        o_x,o_y = filter_points(curve_x,curve_y,35000) #滤点
        for i in range(5): #终点加点避免蓝牙末尾丢包导致丢点
            o_x.append(curve_x[-1])
            o_y.append(curve_y[-1])
        speed = speed_planning(o_x, o_y)

        return curve_x,curve_y,o_x,o_y,speed



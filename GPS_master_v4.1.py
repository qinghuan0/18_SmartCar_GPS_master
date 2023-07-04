import numpy as np
import matplotlib.pyplot as plt

def s_beed(points,amp):
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
                x = np.linspace(-distance / 4, distance / 2, 1000)
            elif end_flg == 1:
                x = np.linspace(0, distance * 3 / 4, 1000)
            else:
                x = np.linspace(0, distance / 2, 1000)

            # 计算对应的 y 坐标点，使用正弦函数，并根据振幅进行调整
            y = amplitude * np.sin((2 * np.pi / distance) * x)

            # 坐标轴变换
            new_x = transform_x(x, y) + x1
            new_y = transform_y(x, y) + y1

            # 绘制正弦曲线的前半个周期
            plt.plot(new_x, new_y, label='Curve')

        else:
            # 生成 x 坐标点，取周期的后半部分
            if start_flg == 1:
                x = np.linspace(-distance / 4, distance / 2, 1000)
            elif end_flg == 1:
                x = np.linspace(0, distance * 3 / 4, 1000)
            else:
                x = np.linspace(0, distance / 2, 1000)

            # 计算对应的 y 坐标点，使用正弦函数，并根据振幅进行调整
            y = - amplitude * np.sin((2 * np.pi / distance) * x)

            # 坐标轴变换
            new_x = transform_x(x, y) + x1
            new_y = transform_y(x, y) + y1

            # 绘制正弦曲线的后半个周期
            plt.plot(new_x, new_y, label='Curve')


    # 遍历相邻的坐标点，绘制余弦曲线和坐标点
    for i in range(len(points) - 2):
        if i % 2 == 0:
            dir = 0
        else:
            dir = 1
        if i == 0:
            start_flg = 1
        else:
            start_flg = 0
        if i == len(points) - 3:
            end_flg = 1
        else:
            end_flg = 0
        x_1 = (points[i][0] + points[i + 1][0]) / 2
        y_1 = (points[i][1] + points[i + 1][1]) / 2
        x_2 = (points[i + 1][0] + points[i + 2][0]) / 2
        y_2 = (points[i + 1][1] + points[i + 2][1]) / 2

        # 绘制曲线
        draw_curve(x_1, y_1, x_2, y_2, amp, dir, start_flg, end_flg)

        # 绘制坐标点
        plt.scatter([points[i][0], points[i+1][0]], [points[i][1], points[i+1][1]], label='Points' + str(i))
        # plt.scatter([x_1, x_2], [y_1, y_2],label='xxx' + str(i), color = 'red')
    plt.scatter(points[-1][0], points[-1][1], label='Points' + str(len(points)))

# 输入坐标点的列表
point = [(110.297709,21.15356), (110.297727,21.153551), (110.297746,21.15354), (110.297764,21.15353)]

# 设置振幅大小
amplitude = 0.00001

# 绘制余弦曲线
s_beed(point, amplitude)

# 设置坐标轴范围
# plt.xlim(110.297709 , max(point[:][0]) )
# plt.ylim(min(point[:][1]) , max(point[:][1]) )

# 添加图例
plt.legend()

# 显示图像
plt.show()

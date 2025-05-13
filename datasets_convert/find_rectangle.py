import cv2
import numpy as np


def find_axis_aligned_bounding_box(points):
    """
    找到给四个定点集的平行于坐标轴的最小外接矩形。
    :param points: 四边形的顶点坐标列表，格式为 [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    :return: 最小外接矩形的四个顶点坐标
    """
    # 将点集转换为 NumPy 数组
    points = np.array(points, dtype=np.float32)

    # 计算边界
    min_x = np.min(points[:, 0])
    max_x = np.max(points[:, 0])
    min_y = np.min(points[:, 1])
    max_y = np.max(points[:, 1])

    # 生成矩形的四个顶点
    bounding_box = [
        [min_x, min_y],  # 左下角
        [max_x, min_y],  # 右下角
        [max_x, max_y],  # 右上角
        [min_x, max_y]  # 左上角
    ]

    return np.array(bounding_box, dtype=np.int32)


# 示例用法
if __name__ == "__main__":
    # 输入四边形的顶点坐标
    quadrilateral_points = [[100, 50], [200, 80], [150, 150], [50, 120]]

    # 找到平行于坐标轴的最小外接矩形
    bounding_box = find_axis_aligned_bounding_box(quadrilateral_points)

    # 输出结果
    print("平行于坐标轴的最小外接矩形的四个顶点坐标：")
    print(bounding_box)

    # 可视化结果（可选）
    img = np.zeros((300, 300, 3), dtype=np.uint8)  # 创建空白图像
    cv2.drawContours(img, [np.array(quadrilateral_points)], -1, (0, 255, 0), 2)  # 绘制四边形
    cv2.drawContours(img, [bounding_box], -1, (255, 0, 0), 2)  # 绘制最小外接矩形
    cv2.imshow("Result", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
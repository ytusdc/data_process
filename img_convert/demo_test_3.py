import cv2
import numpy as np
from scipy.spatial import ConvexHull

def fit_quadrilateral_to_mask(mask, num_keypoints=4):
    """
    从分割掩码中找到一个四边形来尽量拟合分割区域，不要求完全包含。

    参数:
        mask (numpy.ndarray): 二值化的分割掩码图像，形状为 (H, W)，值为 0 或 255。
        num_keypoints (int): 用于拟合的关键点数量，默认为 4。

    返回:
        quadrilateral (numpy.ndarray): 拟合的四边形的四个顶点坐标，形状为 (4, 2)。
    """
    # 确保输入是二值图像
    if len(mask.shape) != 2:
        raise ValueError("输入的掩码必须是二值图像（单通道）。")

    # 提取轮廓
    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        raise ValueError("未在掩码中找到任何轮廓，请检查输入数据。")

    # 获取最大的轮廓（假设只有一个目标）
    largest_contour = max(contours, key=cv2.contourArea)

    # 将轮廓转换为点集
    points = largest_contour.reshape(-1, 2)

    # 计算凸包
    hull = ConvexHull(points)
    hull_points = points[hull.vertices]

    # 从凸包中选择关键点
    if len(hull_points) > num_keypoints:
        step = len(hull_points) // num_keypoints
        selected_points = hull_points[::step][:num_keypoints]
    else:
        selected_points = hull_points

    # 使用几何方法拟合四边形
    def fit_quadrilateral(points):
        from itertools import combinations

        # 对点进行排序以形成四边形
        center = np.mean(points, axis=0)
        angles = np.arctan2(points[:, 1] - center[1], points[:, 0] - center[0])
        sorted_points = points[np.argsort(angles)]

        # 定义直线方程：y = kx + b
        def line_equation(p1, p2):
            if p2[0] == p1[0]:  # 避免除以零的情况
                return None, p1[0]  # 垂直线，返回 None 和 x 值
            k = (p2[1] - p1[1]) / (p2[0] - p1[0])
            b = p1[1] - k * p1[0]
            return k, b

        # 计算两条直线的交点
        def intersection(line1, line2):
            k1, b1 = line1
            k2, b2 = line2

            if k1 is None:  # 第一条线是垂直线
                x = b1
                y = k2 * x + b2
            elif k2 is None:  # 第二条线是垂直线
                x = b2
                y = k1 * x + b1
            else:  # 两条线都不是垂直线
                x = (b2 - b1) / (k1 - k2)
                y = k1 * x + b1
            return np.array([x, y])

        # 构造四条边的直线方程
        lines = []
        for i in range(len(sorted_points)):
            p1 = sorted_points[i]
            p2 = sorted_points[(i + 1) % len(sorted_points)]
            lines.append(line_equation(p1, p2))

        # 计算交点作为四边形顶点
        intersections = []
        for i in range(len(lines)):
            line1 = lines[i]
            line2 = lines[(i + 1) % len(lines)]
            if line1[0] is None or line2[0] is None:  # 特殊处理垂直线
                if line1[0] is None and line2[0] is None:  # 两条垂直线没有交点
                    continue
                elif line1[0] is None:  # 第一条线是垂直线
                    intersections.append(intersection(line1, line2))
                else:  # 第二条线是垂直线
                    intersections.append(intersection(line2, line1))
            else:
                intersections.append(intersection(line1, line2))

        return np.array(intersections).astype(int)

    quadrilateral = fit_quadrilateral(selected_points)

    return quadrilateral

# 示例用法
if __name__ == "__main__":
    # 创建一个简单的掩码示例
    # mask = np.zeros((200, 200), dtype=np.uint8)
    # cv2.rectangle(mask, (50, 50), (150, 150), 255, -1)  # 绘制一个正方形
    # cv2.line(mask, (70, 70), (130, 130), 0, 30)         # 添加一些干扰

    mask = cv2.imread("../datasets_img_visual/1.jpg", cv2.COLOR_BGR2GRAY)
    # mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)  # 3通道转二值化
    # 找到一个四边形来尽量拟合分割区域
    try:
        quadrilateral = fit_quadrilateral_to_mask(mask)
        print("拟合的四边形顶点坐标：")
        print(quadrilateral)

        # 可视化结果
        image = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        for i in range(len(quadrilateral)):
            p1 = tuple(quadrilateral[i])
            p2 = tuple(quadrilateral[(i + 1) % len(quadrilateral)])
            cv2.line(image, p1, p2, (0, 255, 0), 2)
        cv2.imshow("Fitted Quadrilateral", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"发生错误：{e}")
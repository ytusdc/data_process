import cv2
import numpy as np
from scipy.spatial import ConvexHull

def fit_quadrilateral_to_polygon(mask):
    """
    从分割掩码中找到一个四边形来尽量拟合分割区域的多边形。

    参数:
        mask (numpy.ndarray): 二值化的分割掩码图像，形状为 (H, W)，值为 0 或 255。

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

    # 使用旋转卡壳法找到最小包围四边形
    def min_area_quad(points):
        from shapely.geometry import Polygon

        # 初始化最小面积和对应的四边形
        min_area = float('inf')
        best_quad = None

        # 遍历每一条边作为基线
        for i in range(len(points)):
            p1 = points[i]
            p2 = points[(i + 1) % len(points)]

            # 计算垂直于这条边的方向向量
            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            normal = np.array([-dy, dx])

            # 归一化方向向量
            normal = normal / np.linalg.norm(normal)

            # 计算所有点到这条边的距离
            distances = np.dot(points - p1, normal)

            # 找到距离的最大值和最小值
            min_dist = np.min(distances)
            max_dist = np.max(distances)

            # 计算当前四边形的面积
            edge_length = np.linalg.norm(p2 - p1)
            current_area = edge_length * (max_dist - min_dist)

            # 如果当前面积更小，则更新最佳四边形
            if current_area < min_area:
                min_area = current_area
                # 构造四边形的四个顶点
                v1 = p1 + min_dist * normal
                v2 = p1 + max_dist * normal
                v3 = p2 + max_dist * normal
                v4 = p2 + min_dist * normal
                best_quad = np.array([v1, v2, v3, v4])

        return best_quad

    # 找到最小包围四边形
    quad = min_area_quad(hull_points)

    return quad.astype(int)

# 示例用法
if __name__ == "__main__":
    # 创建一个简单的掩码示例
    # mask = np.zeros((200, 200), dtype=np.uint8)
    # cv2.rectangle(mask, (50, 50), (150, 150), 255, -1)  # 绘制一个正方形
    # cv2.line(mask, (70, 70), (130, 130), 0, 30)         # 添加一些干扰

    mask = cv2.imread("../datasets_img_visual/1.jpg", cv2.COLOR_BGR2GRAY)
    # 找到一个四边形来尽量拟合分割区域的多边形
    try:
        quadrilateral = fit_quadrilateral_to_polygon(mask)
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
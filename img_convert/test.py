import cv2
import numpy as np

def approximate_quadrilateral(mask, epsilon_factor=0.02):
    """
    从分割掩码中找到一个四边形来尽量拟合分割区域。

    参数:
        mask (numpy.ndarray): 二值化的分割掩码图像，形状为 (H, W)，值为 0 或 255。
        epsilon_factor (float): 多边形近似的精度因子，值越小越接近原始轮廓，默认为 0.02。

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

    # 多边形近似
    epsilon = epsilon_factor * cv2.arcLength(largest_contour, True)
    approx_polygon = cv2.approxPolyDP(largest_contour, epsilon, True)

    # 如果近似多边形的顶点数大于 4，则进一步简化为四边形
    while len(approx_polygon) > 4:
        epsilon_factor *= 1.1  # 增加精度因子以减少顶点数
        epsilon = epsilon_factor * cv2.arcLength(largest_contour, True)
        approx_polygon = cv2.approxPolyDP(largest_contour, epsilon, True)

    # 如果顶点数少于 4，则重复使用最远点扩展到四边形
    if len(approx_polygon) < 4:
        approx_polygon = cv2.convexHull(approx_polygon)

    # 确保返回的是四边形
    quadrilateral = approx_polygon.reshape(-1, 2)

    return quadrilateral

# 示例用法
if __name__ == "__main__":
    # # 创建一个简单的掩码示例
    # mask = np.zeros((200, 200), dtype=np.uint8)
    # cv2.rectangle(mask, (30, 50), (40, 150), 255, -1)  # 绘制一个正方形
    # cv2.line(mask, (70, 70), (130, 130), 0, 30)         # 添加一些干扰

    # 读取mask为二值化数据
    mask = cv2.imread("../datasets_img_visual/1.jpg", cv2.COLOR_BGR2GRAY)
    # mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)  # 3通道转二值化

    # 找到一个四边形来尽量拟合分割区域
    quadrilateral = approximate_quadrilateral(mask)

    print("拟合的四边形顶点坐标：")
    print(quadrilateral)

    # 可视化结果
    image = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    if quadrilateral is not None:
        for i in range(len(quadrilateral)):
            p1 = tuple(quadrilateral[i])
            p2 = tuple(quadrilateral[(i + 1) % len(quadrilateral)])
            cv2.line(image, p1, p2, (0, 255, 0), 2)
        cv2.imshow("Approximated Quadrilateral", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
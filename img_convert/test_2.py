import cv2
import numpy as np
import json

# # 示例多边形顶点
# points = np.array([[34, 348], [118, 331], [158, 292], [317, 284],
#                    [340, 241], [426, 240], [450, 273], [551, 256],
#                    [683, 222], [722, 248], [752, 249], [784, 333]], dtype=np.int32)
#
# json_file = "/home/ytusdc/Pictures/meimian/Snipaste_2025-02-18_11-04-02.json"
# with open(json_file, "r") as f:
#     json_data = json.load(f)
#
# # points = np.array(json_data["shapes"][0]["points"], dtype=np.int32).reshape((-1, 1, 2))
# points = np.array(json_data["shapes"][0]["points"], dtype=np.int32)
#
# # 计算凸包
# hull = cv2.convexHull(points)
#
# # 如果凸包点数大于4，选择前4个点作为四边形
# if len(hull) > 4:
#     hull = hull[:4].reshape(-1, 2)  # 取前4个点
# else:
#     hull = hull.reshape(-1, 2)  # 如果凸包点数小于等于4，直接使用
#
# print("拟合的四边形顶点：")
# print(hull)

import cv2
import numpy as np

# 示例二值掩码图像
mask = np.zeros((500, 500), dtype=np.uint8)
cv2.fillPoly(mask, [np.array([[100, 100], [200, 100], [250, 200], [150, 200]])], 255)

mask = cv2.imread("../datasets_img_visual/1.jpg", cv2.COLOR_BGR2GRAY)

# 检测角点
corners = cv2.goodFeaturesToTrack(mask, maxCorners=4, qualityLevel=0.01, minDistance=50)
corners = np.int0(corners).reshape(-1, 2)

print("拟合的四边形顶点：")
print(corners)

# 可视化结果
image = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
if corners is not None:
    for i in range(len(corners)):
        p1 = tuple(corners[i])
        p2 = tuple(corners[(i + 1) % len(corners)])
        cv2.line(image, p1, p2, (0, 255, 0), 2)
    cv2.imshow("Approximated Quadrilateral", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
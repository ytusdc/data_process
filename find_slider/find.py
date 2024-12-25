import cv2
import numpy as np


def find_slider_and_gap(image_path):
    # 读取图片
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image not found or unable to read")

    # 转换为灰度图像
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # 使用高斯模糊减少噪声
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # 使用Canny边缘检测
    edges = cv2.Canny(blurred, 50, 150)

    # 使用轮廓检测找到滑块和缺口
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 找到最大的两个轮廓（假设滑块和缺口是最明显的两个轮廓）
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:2]

    if len(contours) < 2:
        raise ValueError("Not enough contours found")

    # 计算轮廓的边界框
    slider_box = cv2.boundingRect(contours[0])
    gap_box = cv2.boundingRect(contours[1])

    # 计算滑块和缺口的中心点
    slider_center = (slider_box[0] + slider_box[2] // 2, slider_box[1] + slider_box[3] // 2)
    gap_center = (gap_box[0] + gap_box[2] // 2, gap_box[1] + gap_box[3] // 2)

    # 计算滑块和缺口在X轴上的距离
    distance_x = abs(slider_center[0] - gap_center[0])

    # 绘制边界框和中心点
    cv2.rectangle(image, slider_box, (0, 255, 0), 2)
    cv2.rectangle(image, gap_box, (0, 0, 255), 2)
    cv2.circle(image, slider_center, 5, (0, 255, 0), -1)
    cv2.circle(image, gap_center, 5, (0, 0, 255), -1)

    cv2.namedWindow('Result', cv2.WINDOW_NORMAL)
    # 显示结果图像
    cv2.imshow('Result', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return slider_center, gap_center, distance_x


# 示例使用
image_path = './img/01.jpg'
# slider_center, gap_center, distance_x = find_slider_and_gap(image_path)
# print(f"滑块中心坐标: {slider_center}")
# print(f"缺口中心坐标: {gap_center}")
# print(f"滑块和缺口在X轴上的距离: {distance_x}")

img = cv2.imread(image_path)

B,G,R=cv2.split(img)
hsv_img=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
H,S,V=cv2.split(hsv_img)


ret1, thres= cv2.threshold(V, 200, 255, cv2.THRESH_BINARY_INV)
cv2.namedWindow('thres', cv2.WINDOW_NORMAL)
cv2.imshow('thres', thres)
cv2.waitKey(0)
cv2.destroyAllWindows()


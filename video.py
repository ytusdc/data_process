#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-09-19 15:20
Author  : sdc
"""
import os.path

import cv2


path = "/home/ytusdc/file.mp4"
save_path = "/home/ytusdc/fire_img"
# 创建一个VideoCapture对象，参数是视频文件的路径


# 创建视频捕获对象
cap = cv2.VideoCapture(path)  # 替换为你的视频文件路径

# 检查视频是否打开成功
if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

count_frame = 0

num = 123
formatted_num = str(num).zfill(4)
print(formatted_num)  # 输出：0123
while True:
    ret, frame = cap.read()  # 读取一帧

    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    # name = str(count_frame) + ".jpg"

    formatted_name = str(count_frame).zfill(6) + ".jpg"
    img_save_path = os.path.join(save_path, formatted_name)

    if count_frame % 10 == 0:
        cv2.imwrite(img_save_path, frame)
    count_frame += 1


# 释放捕获对象
cap.release()
cv2.destroyAllWindows()





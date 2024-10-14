#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-10-14 16:12
Author  : sdc
"""
"""
Time    : 2024-10-14 15:57
Author  : sdc
"""

import cv2
import os
import numpy as np
import utils.common as common_fun

"""
不同尺寸的图片合成视频，不改变原始图片的大小。
通过在图片周围添加填充（padding）来实现这一点。这样可以确保所有图片都具有相同的尺寸，同时保持原始图片的完整性。
"""
def images_to_video(image_folder, video_name, fps=24):
    # 获取图片列表
    images = common_fun.get_filename_ls(image_folder)

    # 对图片进行排序，以保持正确的顺序

    # 检查图片列表是否为空
    if not images:
        print("没有找到图片文件")
        return

    # 获取图片的最大宽度和高度
    max_width, max_height = 0, 0
    for image in images:
        frame = cv2.imread(os.path.join(image_folder, image))
        h, w, _ = frame.shape
        if w > max_width: max_width = w
        if h > max_height: max_height = h

    # 定义视频编码器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 使用mp4格式
    video = cv2.VideoWriter(video_name, fourcc, fps, (max_width, max_height))

    # 将图片写入视频
    for image in images:
        frame = cv2.imread(os.path.join(image_folder, image))
        h, w, _ = frame.shape

        # 创建一个空白的背景图像
        padded_image = np.zeros((max_height, max_width, 3), dtype=np.uint8)

        # 计算填充的位置
        top = (max_height - h) // 2
        bottom = top + h
        left = (max_width - w) // 2
        right = left + w

        # 将原始图像放置在空白背景的中心
        padded_image[top:bottom, left:right] = frame

        # 写入视频
        video.write(padded_image)

    # 完成所有操作后释放视频编写器
    video.release()
    print(f"视频已保存为 {video_name}")


if __name__ == '__main__':
    # 使用示例
    image_folder = '/home/ytusdc/codes_zkyc/ultralytics_yolov5/runs/detect/exp7'  # 图片文件夹路径
    video_name = 'output.mp4'  # 输出视频文件名
    fps = 1  # 帧率
    images_to_video(image_folder, video_name, fps)
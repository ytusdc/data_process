#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import cv2
import numpy as np
from pathlib import Path
import argparse
import yaml
from tqdm import tqdm

class OpencvSeg:
    def __init__(self, modelpath,
                 id_class_dict=None,    # 暂时没用到
                 input_size=(480, 480)  # (w, h) 模型的输入尺寸, 分割模型输入输出同尺寸
                 ):
        self.classes = ['background', 'coal']   # 现在的分割模型只有这两类，后续模型如果更改这里要做相应更改
        self.net = cv2.dnn.readNet(modelpath)
        self.input_size = input_size
        # 可选：颜色映射, 只有四类，可以自己增加
        # 创建一个颜色查找表（LUT），例如为不同的类别分配不同的颜色(b, g, r)
        self.colors = [(0, 0, 0), (0, 0, 255), (0, 255, 0), (255, 0, 0)]  # 黑、红、绿、蓝

    # 图片仿射变换
    def warpAffine(self, ori_img):
        from_height, from_width, _ = ori_img.shape
        to_height, to_width = self.input_size[1], self.input_size[0]
        # 仿射变换
        scale_x = to_width / from_width
        scale_y = to_height / from_height
        scale = min(scale_x, scale_y)
        ox = (-scale * from_width + to_width + scale - 1) * 0.5
        oy = (-scale * from_height + to_height + scale - 1) * 0.5
        k = 1 / scale
        i2d = np.array([[scale, 0, ox], [0, scale, oy]])
        d2i = np.array([[k, 0, -k * ox], [0, k, -k * oy]])
        image_warp = cv2.warpAffine(ori_img, i2d, (to_width, to_height))
        # 仿射变换矩阵
        self.i2d = i2d
        self.d2i = d2i  # 逆变换
        return  image_warp

    def predict(self, image):
        input_image = self.warpAffine(image)
        blob = cv2.dnn.blobFromImage(input_image, 1 / 255.0, self.input_size, [0, 0, 0], swapRB=True, crop=False)
        self.net.setInput(blob)
        outs_tuple = self.net.forward(self.net.getUnconnectedOutLayersNames())
        output = outs_tuple[0]
        # 获取输出的形状
        num_classes, out_height, out_width = output.shape[1:4]
        # 如果是多类别分割，取每个像素的最大值作为类别
        if num_classes > 1:
            class_map = np.argmax(output[0], axis=0).astype(np.uint8)
        else:
            # 对于二分类，应用阈值
            class_map = (output[0, 0] > 0.5).astype(np.uint8)
        ori_height, ori_width, _ = image.shape
        class_map = cv2.warpAffine(class_map, self.d2i, (ori_width, ori_height)).astype(np.uint8)

        color_mask = np.zeros_like(image)
        for i in range(num_classes):
            index = i % len(self.colors)   # 避免颜色值没有类别多的情况
            color_mask[class_map == i] = self.colors[index]

        # 将颜色蒙版与原始图像混合
        alpha = 0.3  # 蒙版透明度
        blended = cv2.addWeighted(image, 1 - alpha, color_mask, alpha, 0)
        return blended

    # 原来的推理，结果一致
    def predict_ori(self, image):
        input_image = self.warpAffine(image)
        blob = cv2.dnn.blobFromImage(input_image, 1 / 255.0, self.input_size, [0, 0, 0], swapRB=True, crop=False)
        self.net.setInput(blob)
        outs_tuple = self.net.forward(self.net.getUnconnectedOutLayersNames())
        output = outs_tuple[0]
        out = outs_tuple[0][0]
        mask = np.zeros((self.input_size[0], self.input_size[1], 3))
        mask[out[0] < out[1]] = [0, 0, 255]
        ori_height, ori_width, _ = image.shape
        mask_ = cv2.warpAffine(mask, self.d2i, (ori_width, ori_height)).astype(np.uint8)
        blended = cv2.addWeighted(image, 0.7, mask_, 0.3, 0)
        return blended

def get_id_cls_dict(yaml_file_path):
    if yaml_file_path is None:
        return None
    def read_yaml(file_path):
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
        return data
    yaml_dict = read_yaml(yaml_file_path)
    return yaml_dict["names"]

def traverse_folder(folder_path):
    if Path(folder_path).is_file() and folder_path.endswith(".mp4"):
        return [folder_path]   # 如果传入的是视频文件，则直接返回

    file_path_ls = []
    for file_path in Path(folder_path).glob('**/*'):
        if file_path.is_file() and str(file_path).endswith(".mp4"):
            # print(file_path)
            file_path_ls.append(str(file_path))
    return file_path_ls

def get_filepath_ls(data_dir, suffix=None):
    """
    过滤特定类型，获取文件全路径列表， 默认获取图片文件列表
    Args:
        data_dir:
        suffix: None 默认过滤图片文件
    Returns:
    """
    if suffix is None:
        # suffix = ('.jpg', '.png', '.jpeg', '.bmp')
        suffix = ['.jpg', '.png', '.jpeg', '.bmp']
    if Path(data_dir).is_file() and data_dir.lower().endswith(suffix):
        # data_dir 本身是一个图片文件
        return [data_dir]

    # 过滤掉 ‘.’开头的隐藏文件, 有的情况下会出现，大部分情况不会，以防万一
    filter_file_ls = os.listdir(data_dir)
    for i in range(len(filter_file_ls) - 1, -1, -1):  # for i in range(0, num_list.__len__())[::-1]
        if filter_file_ls[i].startswith('.'):
            filter_file_ls.pop(i)
    file_ls = []
    if isinstance(suffix, str):
        file_ls = [os.path.join(data_dir, x) for x in filter_file_ls if x.lower().endswith(suffix)]
    elif isinstance(suffix, list):
        file_ls = [os.path.join(data_dir, x) for x in filter_file_ls if os.path.splitext(x.lower())[-1] in suffix]
    return sorted(file_ls)  # 排序， 不同平台保持顺序一致

def video_infer(model_net, video_path, save_dir, interval=1):
    # 创建视频捕获对象, VideoCapture对象
    cap = cv2.VideoCapture(video_path)
    # 检查视频是否打开成功
    if not cap.isOpened():
        print(f"Error: Could not open video: {video_path}")
        return
    # 获取视频总帧数
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    count_frame = 0
    cv2.namedWindow("out_seg", 0)
    while True:
        ret, frame = cap.read()  # 读取一帧
        if not ret:
            print("Can't receive frame (stream end?). break readvieo ...")
            break
        if count_frame % interval == 0:
            result_img = model_net.predict(frame)

            # 保存分割结果
            formatted_name = str(count_frame).zfill(6) + ".jpg"
            img_save_path = os.path.join(save_dir, formatted_name)
            cv2.imwrite(img_save_path, result_img)

            # 显示分割结果
            cv2.imshow('out_seg', result_img)
            cv2.waitKey(1)
        count_frame += 1
    # 释放捕获对象
    cap.release()

# 煤流测试
def begin_video_infer(model_path, video_path, save_dir, id_class_dict=None, frame_interval=20):

    """
    Args:
        model_path:  onnx 模型路径
        video_path: video dir/video file,
                     video dir 存放目录：会遍历整个目录的video， 并且建立相应的目录结构存放检测结果
                     video file 文件路径： video 文件路径
        save_dir:
        id_class_dict:
        frame_interval:
    Returns:
    """

    model_Net = OpencvSeg(model_path, id_class_dict=id_class_dict)  # 模型
    # 检测video文件
    if video_path.endswith(('.mp4', 'avi')):
        video_path = video_path
        video_name = Path(video_path).stem
        result_save_dir = Path(save_dir, video_name)
        Path(result_save_dir).mkdir(parents=True, exist_ok=True)
        print(f"current process: {video_path}")
        video_infer(model_Net, video_path, result_save_dir, interval=frame_interval)
    else:   # 遍历video_dir目录
        video_file_ls = traverse_folder(video_path)
        for video_file in tqdm(sorted(video_file_ls)):
            parent_dir = str(Path(video_file).parent).strip('/')
            video_name = Path(video_file).stem
            middle_dir = parent_dir.replace(video_path.strip('/'), "").strip('/')
            result_save_dir = Path(save_dir, middle_dir, video_name)
            Path(result_save_dir).mkdir(parents=True, exist_ok=True)
            print(f"current process: {video_file}")
            video_infer(model_Net, video_file, result_save_dir, interval=frame_interval)

def begin_img_infer(model_path, img_dir, save_dir, id_class_dict=None):
    """
    Args:
        model_path: onnx 模型路径
        img_dir:  img_dir / img_file_path
                  img_dir 图片存放目录
                  video file 文件路径： 图片文件路径
        save_dir:
        id_class_dict:
    Returns:

    """
    img_path_ls = get_filepath_ls(img_dir)
    model_Net = OpencvSeg(model_path, id_class_dict=id_class_dict)
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    for img_path in tqdm(sorted(img_path_ls)):
        image = cv2.imread(img_path)
        if image is None:
            continue
        result_img = model_Net.predict(image)
        img_name = Path(img_path).name
        img_save_path = os.path.join(save_dir, img_name)
        cv2.imwrite(img_save_path, result_img)
        cv2.imshow('out_det', image)
        cv2.waitKey(0)

def main():
    # img param, 可以单张图片或者图片文件夹
    img_dir = '/path/to/img'

    # video param
    model_path = "/home/ytusdc/codes_zkyc/svn_Release/源模型/语义分割/皮带状态/煤流检测_v2.onnx"

    # model param
    video_path = "/home/ytusdc/测试数据/01000000772000000_clip_no.mp4"
    # yaml_file = None
    # id_class_dict = get_id_cls_dict(yaml_file)
    id_class_dict = None

    save_dir = "/home/ytusdc/测试数据/result_no"

    begin_video_infer(model_path, video_path, save_dir, id_class_dict=id_class_dict, frame_interval=1)


if __name__ == "__main__":
    main()

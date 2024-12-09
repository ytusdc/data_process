#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-09-19 15:20
Author  : sdc
"""
import cv2
import os
import sys
from pathlib import Path
import numpy as np
import argparse
import yaml
from tqdm import tqdm

class OpencvDetect:
    def __init__(self, modelpath,
                 id_class_dict=None,
                 nmsThreshold=0.45,
                 confThreshold=0.4,
                 input_size=(640, 640)
                 ):
        '''
        yamlfile： 读取 id 对应类别名， 得到 self.id_class_dict
        input_size： 模型输入的尺寸， yolo 默认是 (640, 640)
        '''
        self.nmsThreshold = nmsThreshold
        self.confThreshold = confThreshold
        self.input_size = input_size
        self.net = cv2.dnn.readNet(modelpath)
        self.id_class_dict = id_class_dict

        self.colors = [(255, 0, 255), (0, 255, 0), (0, 0, 255), (0, 255, 255), (0, 100, 200), (255, 0, 0),
                       (100, 0, 200), (0, 255, 50)]
        if self.id_class_dict is None:
            print(f"id_class_dict 对应表为 None， 类别将会以 id 显示")
        else:
            for key, value in id_class_dict.items():
                print(f" {key} : {value}")

    def drawPred(self, image, classId, conf, pt_top_left, pt_bottom_right):
        font = cv2.FONT_HERSHEY_SIMPLEX
        top_left_x, top_left_y = pt_top_left
        cv2.rectangle(image, pt_top_left, pt_bottom_right, self.colors[classId], thickness=2)
        label = '%.2f' % conf
        label = '%s' % (self.id_class_dict[classId] if self.id_class_dict is not None else classId)+" "+label
        labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.1, 1)
        text_origin = (top_left_x - 3, top_left_y - int(labelSize[1] * 1.5))
        end = (top_left_x + int(labelSize[0] * 0.85), top_left_y)
        cv2.rectangle(image, text_origin, end, self.colors[classId], cv2.FILLED)
        cv2.putText(image, label, (top_left_x, top_left_y - 9), font, 0.9, (0, 0, 0), thickness=1)#3

    # 图片仿射变换
    def warpAffine(self, ori_img):
        from_height, from_width, _ = ori_img.shape
        to_height, to_width = self.input_size
        # 仿射变换
        scale_x = to_width / from_width
        scale_y = to_height / from_height
        scale = min(scale_x, scale_y)
        ox = (-scale * from_width + to_width + scale - 1) * 0.5
        oy = (-scale * from_height + to_height + scale - 1) * 0.5
        k = 1 / scale
        i2d = np.array([[scale, 0, ox],[0, scale, oy]])
        d2i = [k, 0, -k*ox, 0, k, -k*oy]
        input_image = cv2.warpAffine(ori_img, i2d, (to_width, to_height))
        # 仿射变换矩阵
        self.i2d = i2d
        self.d2i = d2i  # 逆变换
        return  input_image

    # 仿射逆变换
    def unwarpAffine(self, cxywhn):
        center_x = int(self.d2i[0] * cxywhn[0] + self.d2i[2])
        center_y = int(self.d2i[4] * cxywhn[1] + self.d2i[5])
        width = int(cxywhn[2] * self.d2i[0])
        height = int(cxywhn[3] * self.d2i[0])
        box = [center_x, center_y, width, height]
        return box

    def cxywh2xywh(self, cxywh):
        center_x, center_y, width, height = cxywh
        top_left_x = int(center_x - width / 2)
        top_left_y = int(center_y - height / 2)
        return [top_left_x, top_left_y, width, height]

    def xywh2xyxy(self, xywh):
        x1, y1, width, height = xywh
        x2 = int(x1 + width)
        y2 = int(y1 + height)
        return [x1, y1, x2, y2]

    def postprocess(self, outputs):
        det_results = []
        classIds = []
        bboxes = []
        scores=[]
        outputs_arry = outputs[0]

        for output in outputs_arry:
            for detect in output:
                obj_pro = detect[4]
                class_pro = detect[5:]
                class_Index = np.argmax(class_pro)
                score = obj_pro * class_pro[class_Index]
                if score < self.confThreshold:
                    continue
                cxywh = self.unwarpAffine(detect[:4])
                box = self.cxywh2xywh(cxywh)
                bboxes.append(box)
                scores.append(score)
                classIds.append(class_Index)

        indices = cv2.dnn.NMSBoxes(bboxes, scores, self.confThreshold, self.nmsThreshold)
        for i in indices:
            box_xyxy = self.xywh2xyxy(bboxes[i])
            classId=classIds[i]
            conf=scores[i]
            det_results.append([box_xyxy, classId, conf])
        return det_results

    def predict(self, image, is_draw=True):
        input_image = self.warpAffine(image)
        # 从图像数据创建一个 blob
        blob = cv2.dnn.blobFromImage(input_image, 1/255.0, self.input_size, [0, 0, 0], swapRB=True, crop=False)
        # 设置网络的输入
        self.net.setInput(blob)
        # 进行前向推理
        outputs = self.net.forward(self.net.getUnconnectedOutLayersNames())
        det_results_ls = self.postprocess(outputs)

        # 绘制 box
        for det in det_results_ls:
            x1, y1, x2, y2 = det[0]
            pt1 = (x1, y1)
            pt2 = (x2, y2)
            classId = det[1]
            conf = det[2]
            self.drawPred(image, classId, conf, pt1, pt2)

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
        suffix = ('.jpg', '.png', '.jpeg', '.bmp')
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

def video_infer(model_net, video_path, save_dir, interval=20):
    # 创建视频捕获对象, VideoCapture对象
    cap = cv2.VideoCapture(video_path)
    # 检查视频是否打开成功
    if not cap.isOpened():
        print(f"Error: Could not open video: {video_path}")
        return
    # 获取视频总帧数
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    count_frame = 0
    while True:
        ret, frame = cap.read()  # 读取一帧
        if not ret:
            print("Can't receive frame (stream end?). break readvieo ...")
            break
        formatted_name = str(count_frame).zfill(6) + ".jpg"
        img_save_path = os.path.join(save_dir, formatted_name)
        if count_frame % interval == 0:
            model_net.predict(frame)
            cv2.imwrite(img_save_path, frame)
            cv2.imshow('out_det', frame)
            cv2.waitKey(1)
        count_frame += 1
    # 释放捕获对象
    cap.release()

def get_id_cls_dict(yaml_file_path):
    if yaml_file_path is None:
        return None
    def read_yaml(file_path):
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
        return data
    yaml_dict = read_yaml(yaml_file_path)
    return yaml_dict["names"]

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
    model_Net = OpencvDetect(model_path, id_class_dict=id_class_dict)
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
    img_path_ls = get_filepath_ls(img_dir)
    model_Net = OpencvDetect(model_path, id_class_dict=id_class_dict)
    Path(save_dir).mkdir(parents=True, exist_ok=True)
    for img_path in tqdm(sorted(img_path_ls)):
        image = cv2.imread(img_path)
        if image is None:
            continue
        model_Net.predict(image)
        img_name = Path(img_path).name
        img_save_path = os.path.join(save_dir, img_name)
        cv2.imwrite(img_save_path, image)
        cv2.imshow('out_det', image)
        cv2.waitKey(1)

def main():

    # img param
    img_dir = '/home/ytusdc/测试数据/car_1'
    img_dir = '/home/ytusdc/测试数据/00010003439000000'
    img_dir = '/home/ytusdc/Pictures/22.jpeg'
    # video param
    video_dir = "/home/ytusdc/测试数据/10.11/"
    video_dir = "/home/ytusdc/测试数据/192.100.10.59/00010003630000000.mp4"
    video_dir = "/home/ytusdc/测试数据/clip.avi"
    video_dir = "/home/ytusdc/Pictures/yiwu.mp4"
    # video_dir = "/home/ytusdc/测试数据/10.11/20241010000825-20241010110825/output_segment_2.avi"

    # common param
    model_path = "/home/ytusdc/codes_zkyc/svn_Release/源模型/物体检测/皮带状态/belt_v1.onnx"
    yaml_file = "/home/ytusdc/codes_zkyc/svn_Release/源模型/物体检测/皮带状态/id_class.yaml"

    # model_path = "/home/ytusdc/codes_zkyc/svn_Release/源模型/物体检测/车辆检测/v1.1/yolov5_car_v1.1.onnx"
    # # model_path = "/home/ytusdc/codes_zkyc/svn_Release/源模型/物体检测/动火检测/v1.1/spark_v1.1.onnx"
    # yaml_file = "/home/ytusdc/codes_zkyc/svn_Release/源模型/物体检测/动火检测/v1.1/id_class.yaml"
    # yaml_file = "/home/ytusdc/codes_zkyc/svn_Release/源模型/物体检测/车辆检测/v1.1/id_class.yaml"
    id_class_dict = get_id_cls_dict(yaml_file)
    # frame_interval = 20  # 间隔帧

    save_dir = '/home/ytusdc/测试数据/result'
    # save_dir = '/home/ytusdc/测试数据/第一批/result_det'
    # save_dir = "/home/ytusdc/测试数据/10.11/"
    begin_video_infer(model_path, video_dir, save_dir, id_class_dict=id_class_dict, frame_interval=1)

    # begin_img_infer(model_path, img_dir, save_dir, id_class_dict)

if __name__ == '__main__':
    main()






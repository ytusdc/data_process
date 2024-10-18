#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")

import os
import argparse
import cv2
import matplotlib
from pathlib import Path

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from tqdm import tqdm

from utils import *

"""
imgs_dir: 原始图片所在路径
annos_dir： 标签文件所在路径
imgs_save_dir： 绘制 bbox后的img存储位置
yaml_file: yolo 标签对应类别的文件
bgr： 颜色值格式为bgr，使用opencv绘图颜色值是bgr， 如果是rgb格式颜色值需要做相应转换
"""
def draw_image(imgs_dir, annos_dir,  imgs_save_dir, yaml_file=None, bgr=True):
    assert os.path.exists(imgs_dir), "image path:{} dose not exists".format(imgs_dir)
    assert os.path.exists(annos_dir), "annotation path:{} does not exists".format(annos_dir)
    if not os.path.exists(imgs_save_dir):
        os.makedirs(imgs_save_dir)
    # img_id_dict = {Path(i).stem: os.path.join(imgs_dir, i) for i in os.listdir(imgs_dir) if os.path.splitext(i)[-1] in img_type}
    # label_id_dict = {Path(i).stem: os.path.join(annos_dir, i) for i in os.listdir(annos_dir) if os.path.splitext(i)[-1]=='.txt'}

    img_id_dict = common_fun.get_id_path_dict(imgs_dir)
    label_id_dict = common_fun.get_id_path_dict(annos_dir, suffix='.txt')
    category_id_dict = dict()
    if yaml_file is not None:
        category_id_dict = get_id_cls_dict(yaml_file)

    for id in tqdm(label_id_dict.keys()):
        label_file = label_id_dict[id]
        img_file = img_id_dict[id]
        filename = os.path.basename(img_file)
        img = cv2.imread(img_file)
        if img is None:
            print(f"{img_file} read is None")
            return

        objects = utils_yolo_opt.parse_yolo(label_file, img.shape)
        for obj in objects:
            category_id = int(obj[0])  # category_id 用来得到类别的颜色值
            if yaml_file is not None:
                category_name = category_id_dict[category_id]
            else:
                category_name = str(category_id)

            xmin = int(float(obj[1][0]))
            ymin = int(float(obj[1][1]))
            xmax = int(float(obj[1][2]))
            ymax = int(float(obj[1][3]))

            if bgr:
                color = get_color_bgr(category_id)
            else:
                color = get_color_rgb(category_id)

            cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, thickness=2)
            cv2.putText(img, category_name, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, thickness=2)
            cv2.imwrite(os.path.join(imgs_save_dir, filename), img)

if __name__ == '__main__':
    """
    脚本说明：
        该脚本用于yolo标注格式（.txt）的标注框可视化
    参数明说：
        imgs-dir: 图片数据路径
        label-dir: yolo标注文件路径
        save-dir: 绘制bbox后，图片存储路径
        yaml-file： id_class.yaml 文件路径，可以为None，则以yolo中类别id作为类别名进行visual
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--imgs-dir', type=str, default=None, help='图片文件路径')
    parser.add_argument('-y', '--yolo-dir', type=str, default=None, help='标签文件路径')
    parser.add_argument('-s', '--save-dir', type=str, default=None, help='图片存储路径')
    parser.add_argument('-f', '--yaml-file', type=str, default=None, help='id 和类别对应的yaml文件，可以为None')
    opt = parser.parse_args()

    input_args = sys.argv[1:]  # 第一个参数是脚本名本身
    if len(input_args) > 0:
        if opt.imgs_dir is None or opt.yolo_dir is None or opt.save_dir is None:
            print(f"imgs-dir/label-dir/save-dir，三个参数必须都不为空，请检查输入, 退出脚本！")
            sys.exit(-1)
        image_path = opt.imgs_dir
        anno_path = opt.label_dir
        img_visual_save_dir = opt.save_dir
        yaml_file = opt.yaml_file
    else:

        image_path = '../datasets_convert/data/images'  # path/to/images
        anno_path = '../datasets_convert/data/labels/yolo'  # path/to/label/yolo
        img_visual_save_dir = '../datasets_img_visual/visual_images/visual_yolo'  # path/to/visual_images
        yaml_file = None  # path/to/id_class_yaml, 可以为None，则以yolo中类别id作为类别名进行visual
        yaml_file = "../datasets_convert/data/labels/yolo/id_classes.yaml"

    draw_image(image_path, anno_path, img_visual_save_dir, yaml_file)



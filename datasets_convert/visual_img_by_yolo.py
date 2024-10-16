#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")

import os
import argparse
from collections import defaultdict
import cv2
import matplotlib
from pathlib import Path

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from tqdm import tqdm
import datetime

from utils import *

category_dict = dict()
every_class_num = defaultdict(int)
category_item_id = -1

def addCatItem(name):
    global category_item_id
    category_item = dict()
    category_item_id += 1
    category_item['id'] = category_item_id
    category_item['name'] = name
    category_dict[name] = category_item_id
    return category_item_id

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
        height, width, _ = img.shape

        objects = utils_yolo_opt.parse_yolo(label_file, height, width)

        for object in objects:
            if yaml_file is not None:
                category_name = category_id_dict[int(object[0])]
            else:
                category_name = str(object[0])

            every_class_num[category_name] += 1
            if category_name not in category_dict:
                category_id = addCatItem(category_name)
            else:
                category_id = category_dict[category_name]
            xmin = int(float(object[1][0]))
            ymin = int(float(object[1][1]))
            xmax = int(float(object[1][2]))
            ymax = int(float(object[1][3]))

            if bgr:
                color = get_color_bgr(category_id)
            else:
                color = get_color_rgb(category_id)

            cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, thickness=2)
            cv2.putText(img, category_name, (xmin - 10, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, thickness=2)
            cv2.imwrite(os.path.join(imgs_save_dir, filename), img)

    # 默认统计信息
    statistics_info()

"""
统计信息，并且绘制柱形图，然后输出结果
"""
def statistics_info():

    # 绘制每种类别个数柱状图
    plt.bar(range(len(every_class_num)), every_class_num.values(), align='center')
    # 将横坐标0,1,2,3,4替换为相应的类别名称
    plt.xticks(range(len(every_class_num)), every_class_num.keys(), rotation=90)
    # 在柱状图上添加数值标签
    for index, (cls, num) in enumerate(every_class_num.items()):
        plt.text(x=index, y=num, s=str(num), ha='center')
        # print(f"{cls}:{num}")

    # 设置x坐标
    plt.xlabel('image class')
    # 设置y坐标
    plt.ylabel('number of images')
    # 设置柱状图的标题
    plt.title('class distribution')
    # 保存柱状图
    now = datetime.datetime.now()
    time_str = now.strftime('%Y%m%d-%H%M%S')
    plt.savefig(f"class_distribution_{time_str}.png")
    # plt.show()


if __name__ == '__main__':
    """
    脚本说明：
        该脚本用于yolo标注格式（.txt）的标注框可视化
    参数明说：
        imgs-dir:图片数据路径
        label-dir:xml标注文件路径
        save-dir:绘制bbox后，图片存储路径
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--imgs-dir', type=str, default=None, help='图片文件路径')
    parser.add_argument('-l', '--label-dir', type=str, default=None, help='标签文件路径')
    parser.add_argument('-s', '--save-dir', type=str, default=None, help='图片存储路径')
    parser.add_argument('-c', '--yaml-file', type=str, default=None, help='id 和类别对应的yaml文件，可以为None')
    opt = parser.parse_args()

    input_args = sys.argv[1:]  # 第一个参数是脚本名本身
    if len(input_args) > 0:
        if opt.imgs_dir is None or opt.label_dir is None or opt.save_dir is None:
            print(f"imgs-dir/label-dir/save-dir，三个参数必须都不为空，请检查输入, 退出脚本！")
            sys.exit(-1)
        image_path = opt.imgs_dir
        anno_path = opt.label_dir
        img_visual_save_dir = opt.save_dir
        yaml_file = opt.yaml_file
    else:
        yaml_file = None
        image_path = 'path/to/yaml/images'
        anno_path = 'path/to/yaml/yolo'
        img_visual_save_dir = 'path/to/yaml/save_img'
        yaml_file = "path/to/yaml"

    draw_image(image_path, anno_path, img_visual_save_dir, yaml_file)
    print(every_class_num)
    print("category nums: {}".format(len(category_dict)))
    print("bbox nums: {}".format(sum(every_class_num.values())))

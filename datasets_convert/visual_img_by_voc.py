#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")
import os
import cv2
from tqdm import tqdm
import argparse

from utils import *

# 类别和对应的id号， id用作绘制box时候的颜色
global_category_id_dict = dict()
global_category_id = -1

"""
生成类别名和id， id是随机的，主要是用作box的颜色设置
"""
def addCatItem(name):
    global global_category_id
    global_category_id += 1
    global_category_id_dict[name] = global_category_id
    return global_category_id

"""
img_file_path: 原始图片文件全路径
xml_file_path： 标签文件全路径
save_dir： 绘制 bbox后的img存储位置
bgr： 颜色值格式为bgr，使用opencv绘图颜色值是bgr， 如果是rgb格式颜色值需要做相应转换
"""
def draw_box(img_file_path, xml_file_path, save_dir, bgr=True):
    objects, _ = utils_xml_opt.parse_xml(xml_file_path)
    if len(objects) == 0:
        print(f"{xml_file_path} have not object")
        return

    img = cv2.imread(img_file_path)
    if img is None:
        print(f"{img_file_path} : imread img is None or imread failed")
        return

    img_filename = os.path.basename(img_file_path)
    visual_img_file = os.path.join(save_dir, img_filename)
    for obj in objects:
        category_name = obj[0]
        if category_name not in global_category_id_dict.keys():
            category_id = addCatItem(category_name)
        else:
            category_id = global_category_id_dict[category_name]

        if bgr:
            color = get_color_bgr(category_id)
        else:
            color = get_color_rgb(category_id)

        xmin = int(float(obj[1][0]))
        ymin = int(float(obj[1][1]))
        xmax = int(float(obj[1][2]))
        ymax = int(float(obj[1][3]))
        cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, thickness=2)
        cv2.putText(img, category_name, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, thickness=1)
        cv2.imwrite(visual_img_file, img)

"""
imgs_dir: 原始图片所在路径
annos_dir： 标签文件所在路径
visual_save_dir： 绘制 bbox后的img存储位置
"""
def draw_image(imgs_dir, annos_dir, visual_save_dir):
    assert os.path.exists(imgs_dir), "image path:{} dose not exists".format(image_path)
    assert os.path.exists(annos_dir), "annotation path:{} does not exists".format(anno_path)
    if not os.path.exists(visual_save_dir):
        os.makedirs(visual_save_dir)

    img_id_path_dict = common_fun.get_id_path_dict(imgs_dir)
    label_id_path_dict = common_fun.get_id_path_dict(annos_dir, suffix=".xml")

    for img_id, img_file in tqdm(img_id_path_dict.items()):
        if img_id not in set(label_id_path_dict.keys()):  # set 查询速度快
            print(f"xml中没有找到对应id： {img_id}")
            continue
        label_file = label_id_path_dict[img_id]
        draw_box(img_file, label_file, visual_save_dir)

if __name__ == '__main__':
    """
    脚本说明：
        该脚本用于voc标注格式（.xml）的标注框可视化
    参数明说：
        imgs-dir:图片数据路径
        label-dir:xml标注文件路径
        save-dir:绘制bbox后，图片存储路径
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--imgs-dir', type=str, default=None, help='图片文件路径')
    parser.add_argument('-l', '--label-dir', type=str, default=None, help='标签文件路径')
    parser.add_argument('-s', '--save-dir', default=None, help='图片存储路径')
    opt = parser.parse_args()

    input_args = sys.argv[1:]  # 第一个参数是脚本名本身
    if len(input_args) > 0:
        if len(input_args) / 2 != 3:
            print(f"必须传入三个参数，请检查输入, 退出脚本！")
            sys.exit(-1)

        image_path = opt.imgs_dir
        anno_path = opt.label_dir
        save_img_dir = opt.save_dir
    else:
        image_path = './data/images'
        anno_path = './data/convert/voc'
        save_img_dir = './data/save'

    draw_image(image_path, anno_path, save_img_dir)

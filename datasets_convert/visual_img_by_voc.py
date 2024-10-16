#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")
import os
import cv2
import matplotlib.pyplot as plt
from tqdm import tqdm
from lxml import etree
from collections import defaultdict
import argparse
import datetime

from utils import *

category_id_dict = dict()
every_class_num = defaultdict(int)
category_item_id = -1

"""
img_file_path: 原始图片文件全路径
xml_file_path： 标签文件全路径
save_dir： 绘制 bbox后的img存储位置
bgr： 颜色值格式为bgr，使用opencv绘图颜色值是bgr， 如果是rgb格式颜色值需要做相应转换
"""
def draw_box(img_file_path, xml_file_path, save_dir, bgr=True):

    with open(xml_file_path) as fid:
        xml_str = fid.read()
    xml_info = etree.fromstring(xml_str.encode('utf-8'))
    xml_info_dict = utils_xml_opt.parse_xml_to_dict(xml_info)

    img = cv2.imread(img_file_path)
    if img is None:
        print(f"{img_file_path} : imread img is None")
        return
    if 'object' in xml_info_dict['annotation'].keys():
        objects = xml_info_dict['annotation']['object']
    else:
        print(f"{xml_file_path} have not object")
        return

    img_filename = os.path.basename(img_file_path)
    visual_img_file = os.path.join(save_dir, img_filename)
    for object in objects:
        category_name = object['name']
        every_class_num[category_name] += 1
        if category_name not in category_id_dict:
            category_id = addCatItem(category_name)
        else:
            category_id = category_id_dict[category_name]

        xmin = int(float(object['bndbox']['xmin']))
        ymin = int(float(object['bndbox']['ymin']))
        xmax = int(float(object['bndbox']['xmax']))
        ymax = int(float(object['bndbox']['ymax']))

        if bgr:
            color = get_color_bgr(category_id)
        else:
            color = get_color_rgb(category_id)
        cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, thickness=2)
        cv2.putText(img, category_name, (xmin, ymin), cv2.FONT_HERSHEY_SIMPLEX, 1, color, thickness=1)
        cv2.imwrite(visual_img_file, img)

def addCatItem(name):
    global category_item_id
    category_item_id += 1
    category_id_dict[name] = category_item_id
    return category_item_id

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
        print("category nums: {}".format(len(category_id_dict)))
        print("bbox nums: {}".format(sum(every_class_num.values())))
    else:
        image_path = './data/images'
        anno_path = './data/convert/voc'
        save_img_dir = './data/save'
    draw_image(image_path, anno_path, save_img_dir)
    print(every_class_num)
    print("category nums: {}".format(len(category_id_dict)))
    print("bbox nums: {}".format(sum(every_class_num.values())))

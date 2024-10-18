#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")

import os
import cv2
import argparse
from tqdm import tqdm

from utils import *

def parse_yolo2voc(image_path, anno_yolo_path, anno_voc_path, yaml_file):
    assert os.path.exists(image_path), "ERROR {} dose not exists".format(image_path)
    assert os.path.exists(anno_yolo_path), "ERROR {} dose not exists".format(anno_yolo_path)
    assert os.path.exists(yaml_file), "ERROR {} dose not exists".format(yaml_file)

    if not os.path.exists(anno_voc_path):
        os.makedirs(anno_voc_path)

    id_class_dict = utils_xml_opt.get_id_class_dict(yaml_file=yaml_file)
    img_id_name_dict = common_fun.get_id_path_dict(image_path)
    label_id_name_dict = common_fun.get_id_path_dict(anno_yolo_path, suffix=".txt")

    for img_id, img_filepath in tqdm(img_id_name_dict.items()):
        if img_id not in set(label_id_name_dict.keys()):  # set 查询速度快
            print(f"xml中没有找到对应id： {img_id}")
            continue

        img_filename = os.path.basename(img_filepath)
        img = cv2.imread(img_filepath)
        shape = img.shape  # (h, w, depth)

        label_filepath =label_id_name_dict[img_id]
        objects_voc = []
        objects_yolo = utils_yolo_opt.parse_yolo(label_filepath, shape)
        for obj in objects_yolo:
            category_id = int(obj[0])
            category_name = id_class_dict[category_id]
            bbox_int = list(map(int, obj[1]))   # voc 格式坐标转 int
            objects_voc.append([category_name, bbox_int])
        utils_xml_opt.save_anno_to_xml(img_filename, shape, objects_voc, anno_voc_path)

if __name__ == '__main__':
    """
    脚本说明：
        本脚本用于将yolo格式的标注文件.txt转换为voc格式的标注文件.xml
    参数说明：
    
       
        image-dir: 图片路径
        yolo-dir : yolo 标注文件路径
        voc-dir  : voc 格式 xml文件保存路径
        yaml-file ： id-class 对应yaml 文件
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--image-dir', type=str, default=None, help='图片文件路径')
    parser.add_argument('-y', '--yolo-dir', type=str, default=None, help='yolo 标注文件路径')
    parser.add_argument('-v', '--voc-dir', type=str, default=None, help='Voc 标注文件存放路径')
    parser.add_argument('-f', '--yaml-file', type=str, default=None, help='yaml 文件')
    opt = parser.parse_args()

    input_args = sys.argv[1:]  # 第一个参数是脚本名本身
    if len(input_args) > 0:
        if len(input_args)/2 != 4:
            print(f"必须传入四个参数，请检查输入, 退出脚本！")
            sys.exit(-1)
        img_dir = opt.image_dir
        yolo_label_dir = opt.yolo_dir
        voc_label_save_dir = opt.voc_dir
        yaml_file = opt.yaml_file
    else:
        img_dir = './data/images'
        yolo_label_dir = './data/labels/yolo'
        voc_label_save_dir = './result/convert/voc'
        yaml_file = './data/labels/yolo/id_classes.yaml'

    parse_yolo2voc(img_dir, yolo_label_dir, voc_label_save_dir, yaml_file)


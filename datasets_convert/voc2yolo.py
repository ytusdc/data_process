#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append("..")

import os
import argparse
from lxml import etree
from tqdm import tqdm
from pathlib import Path

from utils import *

category_set = set()
image_set = set()
bbox_nums = 0

def parser_info(info: dict, only_cat=True, class_indices=None):
    filename = info['annotation']['filename']
    image_set.add(filename)
    objects = []
    width = int(info['annotation']['size']['width'])
    height = int(info['annotation']['size']['height'])

    if 'object' not in info['annotation']:
        print(filename)
        return filename, []

    for obj in info['annotation']['object']:
        obj_name = obj['name']
        category_set.add(obj_name)
        if only_cat:
            continue
        xmin = float(obj['bndbox']['xmin'])
        ymin = float(obj['bndbox']['ymin'])
        xmax = float(obj['bndbox']['xmax'])
        ymax = float(obj['bndbox']['ymax'])
        bbox = utils_yolo_opt.xyxy2xywhn((xmin, ymin, xmax, ymax), (width, height))
        if class_indices is not None:
            obj_category = class_indices[obj_name]
            object = [obj_category, bbox]
            objects.append(object)
    # print(filename)
    return filename, objects

def getClassIndex(xml_files, save_dir, yaml_file=None):

    if yaml_file is not None:
        id_cls_dict = get_id_cls_dict(yaml_file)
    else:
        # 先解析所有xml文件获取所有类别信息 category_set
        for xml_file in xml_files:
            with open(xml_file) as fid:
                xml_str = fid.read()
            xml = etree.fromstring(xml_str)
            info_dict = utils_xml_opt.parse_xml_to_dict(xml)
            parser_info(info_dict, only_cat=True)
        id_cls_dict = dict((k, v) for k, v in enumerate(sorted(category_set)))
        save_yaml_file = os.path.join(save_dir, "id_classes.yaml")
        write_yaml(save_yaml_file, id_cls_dict)

    class_indices_dict = dict((v, k) for k, v in id_cls_dict.items())
    return class_indices_dict

def parseXmlFiles(voc_dir, save_dir, yaml_file=None):
    assert os.path.exists(voc_dir), "ERROR {} does not exists".format(voc_dir)
    if not operate_dir.mkdirs(save_dir):
        print(f"{save_dir} : 文件夹不为空或者文件夹创建失败，请检查, 退出函数！")
        return
    xml_files = common_fun.get_filepath_ls(voc_dir, suffix=".xml")
    class_indices = getClassIndex(xml_files, save_dir, yaml_file)

    for xml_file in tqdm(xml_files):
        with open(xml_file) as f_r:
            xml_str = f_r.read()
        # xml = etree.fromstring(xml_str)
        xml = etree.fromstring(xml_str.encode('utf-8'))
        info_dict = utils_xml_opt.parse_xml_to_dict(xml)
        _, objects = parser_info(info_dict, only_cat=False, class_indices=class_indices)

        #有的xml 中记录的filename和真实数据对不上，因此用 xml文件名,得到保存的yolo文件名
        basename = Path(xml_file).name
        filename = basename
        if len(objects) != 0:
            global bbox_nums
            bbox_nums += len(objects)
            with open(save_dir + "/" + filename.split(".")[0] + ".txt", 'w') as f:
                for obj in objects:
                    f.write(
                        "{} {:.5f} {:.5f} {:.5f} {:.5f}\n".format(obj[0], obj[1][0], obj[1][1], obj[1][2], obj[1][3]))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--voc-dir', type=str, default=None, help='voc 文件路径')
    parser.add_argument('-s', '--save-dir', type=str, default=None, help='yolo 文件存储路径')
    parser.add_argument('-y', '--yaml-file', type=str, default=None, help='yaml 文件')
    opt = parser.parse_args()

    input_args = sys.argv[1:]  # 第一个参数是脚本名本身
    if len(input_args) > 0:
        if opt.voc_dir is None or opt.save_dir is None:
            print("voc 文件路径和转换后文件存储路径不能为空, 退出脚本！")
            sys.exit(-1)
        voc_xml_dir = opt.voc_dir
        yolo_save_dir = opt.save_dir
        yaml_file = opt.yaml_file
    else:
        yaml_file = None
        voc_xml_dir = './data/labels/voc'
        yolo_save_dir = './data/convert/yolo'
        yaml_file = 'path/to/yaml or None'

    parseXmlFiles(voc_xml_dir, yolo_save_dir, yaml_file)
    print("image nums: {}".format(len(image_set)))
    print("category nums: {}".format(len(category_set)))
    print("bbox nums: {}".format(bbox_nums))

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")

import os
import argparse
from tqdm import tqdm
from pathlib import Path

from utils import *

def getClassIndex(xml_files, save_dir, yaml_file=None):

    if yaml_file is not None:
        id_cls_dict = get_id_cls_dict(yaml_file)
    else:
        # 先解析所有xml文件获取所有类别信息 category_set
        category_set = set()
        for xml_file in xml_files:
            objects, _ = utils_xml_opt.parse_xml(xml_file)
            for object in objects:
                object_name = object[0]
                category_set.add(object_name)
        id_cls_dict = dict((k, v) for k, v in enumerate(sorted(category_set)))
        save_yaml_file = os.path.join(save_dir, "id_classes.yaml")
        write_yaml(save_yaml_file, id_cls_dict)

    class_indices_dict = dict((v, k) for k, v in id_cls_dict.items())
    return class_indices_dict

def parse_xml2yolo(voc_dir, save_dir, yaml_file=None):
    assert os.path.exists(voc_dir), "ERROR {} does not exists".format(voc_dir)
    if not operate_dir.mkdirs(save_dir):
        print(f"{save_dir} : 文件夹不为空或者文件夹创建失败，请检查, 程序退出！")
        return
    xml_files = common_fun.get_filepath_ls(voc_dir, suffix=".xml")
    class_indices_dict = getClassIndex(xml_files, save_dir, yaml_file)
    if len(class_indices_dict) == 0:
        print("没有生成用于 yolo 数据转换的 类别名：id ，对应字典，请检查，程序退出!")
        return

    for xml_file in tqdm(xml_files):
        objects_voc, size = utils_xml_opt.parse_xml(xml_file)
        #有的xml 中记录的filename和真实图片文件名对不上，因此用 xml文件名, 得到保存的yolo文件名
        filename = Path(xml_file).name

        objects_yolo = []
        for obj_voc in objects_voc:
            obj_voc_name = obj_voc[0]
            bbox_voc = obj_voc[1]
            obj_category_id = class_indices_dict[obj_voc_name]
            bbox_yolo = utils_yolo_opt.xyxy2xywhn(bbox_voc, size)
            obj_yolo = [obj_category_id, bbox_yolo]
            objects_yolo.append(obj_yolo)

        if len(objects_yolo) != 0:
            with open(save_dir + "/" + filename.split(".")[0] + ".txt", 'w') as f:
                for obj in objects_yolo:
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
        # yaml_file = 'path/to/yaml or None'

    parse_xml2yolo(voc_xml_dir, yolo_save_dir, yaml_file)


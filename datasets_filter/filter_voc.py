#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")

import os
import json
import argparse
import shutil
from tqdm import tqdm
from pathlib import Path
from lxml import etree, objectify

from utils import *

import os
def mkdirs(full_path_dir):
    if not os.path.exists(full_path_dir):
        os.makedirs(full_path_dir)
        return True
    else:
        print(f"{full_path_dir} is exist, please modify save folder")
        return False

def get_include_info(info: dict, include_cls_set):
    """
    Args: 过滤包含 include_cls_set 中（一个或者多个）类别的 info
        info:
        include_cls_set:
    Returns:
    """
    new_objs_list = []
    try:
        for obj in info['annotation']['object']:
            obj_name = obj['name']
            if obj_name in include_cls_set:
                if "part" in obj.keys():
                    obj.pop("part")
                new_objs_list.append(obj)
    except:
        new_objs_list = []
        pass
    info['annotation']['object'] = new_objs_list
    return info

def get_exclude_info(info: dict, exclude_cls_set):
    """
    Args: 过滤不包含 exclude_cls_set 中（全部）类别的 info
        info:
        exclude_cls_set:
    Returns:
    """
    '''
    图片中没有目标object的情况
    '''
    try:
        for obj in info['annotation']['object']:
            obj_name = obj['name']
            if obj_name in exclude_cls_set:
                info['annotation']['object'] = []
                return info
    except:
        info['annotation']['object'] = []
    return info


def parser_retain_info(info: dict, retain_cls_set=None, unretain_cls_set=None):
    """
    得到最终 的类别信息
    Args:
        info:
        retain_cls_set:
        unretain_cls_set:

    Returns:

    """
    if retain_cls_set is None:
        return get_exclude_info(info, unretain_cls_set)
    else:
        return get_include_info(info, unretain_cls_set)


def filterXmlFiles(img_voc_dir, xml_voc_dir, save_dir, filter_include_set=None, filter_exclude_set=None):
    img_save_dir = os.path.join(save_dir, "images")
    xml_save_dir = os.path.join(save_dir, "xml")

    if filter_include_set is not None and filter_exclude_set is not None:
        print("filter_include_set 和 filter_exclude_set 只能有一个不为None")
        return
    if not mkdirs(img_save_dir) or not mkdirs(xml_save_dir):
        return
    if not os.path.exists(img_voc_dir) or not os.path.exists(xml_voc_dir):
        print("VOC dir {JPEGImages} or {Annotations} is not exist, please check")
        return

    xml_files = [os.path.join(xml_voc_dir, i) for i in os.listdir(xml_voc_dir) if os.path.splitext(i)[-1] == '.xml']

    for xml_file in tqdm(xml_files):
        with open(xml_file) as fid:
            xml_str = fid.read()
        xml = etree.fromstring(xml_str.encode('utf-8'))
        info_dict = utils_xml_opt.parse_xml_to_dict(xml)

        retain_info_dict = parser_retain_info(info_dict, retain_cls_set=filter_include_set, unretain_cls_set=filter_exclude_set)
        if len(retain_info_dict['annotation']['object']) <= 0:
            continue

        filename_xml = os.path.basename(xml_file)
        filename_img = retain_info_dict['annotation']['filename']

        ori_img_path = os.path.join(img_voc_dir, filename_img)
        shutil.copy(ori_img_path, img_save_dir)

        save_xml_path = os.path.join(xml_save_dir, filename_xml)
        utils_xml_opt.save_info_dict_to_xml(retain_info_dict, save_xml_path)

'''
voc_dir: voc 数据集路径
img_voc_dir，xml_voc_dir是标准 voc数据集的图片文件和标签文件路径
save_dir： 筛选后的xml的数据保存路径
filter_set： 需要筛选的类
'''

if __name__ == '__main__':

    # img_voc_dir = os.path.join(voc_dir, "JPEGImages")
    # xml_voc_dir = os.path.join(voc_dir, "Annotations")

    xml_voc_dir = "/home/ytusdc/Downloads/SODA10M/data/SSLAD-2D/annotations/val"
    img_voc_dir = "/home/ytusdc/Downloads/SODA10M/data/SSLAD-2D/val"
    save_dir = "/home/ytusdc/Downloads/SODA10M/data/SSLAD-2D/fliter"

    # get_xml_AllClasses(xml_voc_dir)

    # include_cls_set = set(['bicycle', 'car', 'person', 'motorbike'])
    include_cls_set = None
    exclude_cls_set = set(['Pedestrian', 'Cyclist', 'Tricycle'])

    filterXmlFiles(img_voc_dir, xml_voc_dir, save_dir, filter_include_set=include_cls_set, filter_exclude_set=exclude_cls_set)



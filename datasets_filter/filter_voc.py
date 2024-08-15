#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import argparse
import sys
import shutil
from tqdm import tqdm
from pathlib import Path
import utils.utils as utils
from lxml import etree, objectify
import xml.etree.ElementTree as ET

"""
Time    : 2024-08-13 16:32
Author  : sdc
"""
def parse_cls_info(info: dict):
    cls_set = set()
    filename = info['annotation']['filename']
    if 'object' not in info['annotation']:
        print(filename)
        return cls_set
    for obj in info['annotation']['object']:
        obj_name = obj['name']
        cls_set.add(obj_name)
    return cls_set
def get_xml_AllClasses(voc_xml_dir):
    xml_files = [os.path.join(voc_xml_dir, i) for i in os.listdir(voc_xml_dir) if os.path.splitext(i)[-1] == '.xml']
    category_set = set()
    # 先解析所有xml文件获取所有类别信息 category_set
    xml_files = tqdm(xml_files)
    for xml_file in xml_files:
        with open(xml_file) as fid:
            xml_str = fid.read()
        xml = etree.fromstring(xml_str)
        info_dict = parse_xml_to_dict(xml)
        classes_set = parse_cls_info(info_dict)
        category_set.update(classes_set)
    id_cls_dict = dict((k, v) for k, v in enumerate(sorted(category_set)))
    class_indices_dict = dict((v, k) for k, v in id_cls_dict.items())

    for key, value in class_indices_dict.items():
        print(f"{key}:{value}")
    return class_indices_dict

def parse_xml_to_dict(xml):
    """
    将xml文件解析成字典形式，参考tensorflow的recursive_parse_xml_to_dict
    Args:
        xml: xml tree obtained by parsing XML file contents using lxml.etree

    Returns:
        Python dictionary holding XML contents.
    """
    if len(xml) == 0:  # 遍历到底层，直接返回tag对应的信息
        return {xml.tag: xml.text}

    result = {}
    for child in xml:
        child_result = parse_xml_to_dict(child)  # 递归遍历标签信息
        if child.tag != 'object':
            result[child.tag] = child_result[child.tag]
        else:
            if child.tag not in result:  # 因为object可能有多个，所以需要放入列表里
                result[child.tag] = []
            result[child.tag].append(child_result[child.tag])
    return {xml.tag: result}
def dict_to_xml(root_tag, d):
    """
    将字典转换为XML字符串。
    参数:
    - root_tag: XML根标签
    - d: 字典数据
    """
    elem = ET.Element(root_tag)
    def _dict_to_xml(parent, d):
        for k, v in d.items():
            if isinstance(v, dict):
                child = ET.SubElement(parent, k)
                _dict_to_xml(child, v)
            else:
                ET.SubElement(parent, k).text = str(v)

    _dict_to_xml(elem, d)
    return ET.tostring(elem, encoding='utf-8').decode('utf-8')

def parser_retain_info(info: dict, retain_cls_set):
    new_objs_list = []

    objs = info['annotation']['object']
    for obj in info['annotation']['object']:
        obj_name = obj['name']
        if obj_name in retain_cls_set:
            if "part" in obj.keys():
                obj.pop("part")
            new_objs_list.append(obj)
    info['annotation']['object'] = new_objs_list
    return info
def save_anno_to_xml(info_dict, save_path):
    annotation_dict = info_dict['annotation']
    filename = annotation_dict['filename']
    objs = annotation_dict['object']
    size = annotation_dict['size']
    E = objectify.ElementMaker(annotate=False)
    anno_tree = E.annotation(
        E.folder("voc 2012"),
        E.filename(filename),
        E.source(
            E.database("The VOC Database"),
            E.annotation("PASCAL VOC"),
            E.image("flickr")
        ),
        E.size(
            E.width(size['width']),
            E.height(size['height']),
            E.depth(size['depth'])
        ),
        E.segmented(0)
    )
    for obj in objs:
        E2 = objectify.ElementMaker(annotate=False)
        sub_anno_tree = E2.object(
            E.name(obj['name']),
            E.pose(obj['pose']),
            E.truncated('0'),  #有找不到这个标签的
            E.difficult(obj['difficult']),
            E.bndbox(
                E.xmin(obj['bndbox']['xmin']),
                E.ymin(obj['bndbox']['ymin']),
                E.xmax(obj['bndbox']['xmax']),
                E.ymax(obj['bndbox']['ymax'])
            )
        )
        anno_tree.append(sub_anno_tree)
    # anno_path = os.path.join(save_path, filename[:-3] + "xml")
    # etree.ElementTree(anno_tree).write(anno_path, pretty_print=True)
    etree.ElementTree(anno_tree).write(save_path, pretty_print=True)


def filterXmlFiles(img_voc_dir, xml_voc_dir, save_dir, filter_cat_set):
    img_save_dir = os.path.join(save_dir, "image")
    xml_save_dir = os.path.join(save_dir, "xml")
    if not utils.mkdirs(img_save_dir) or not utils.mkdirs(xml_save_dir):
        return

    if not os.path.exists(img_voc_dir) or not os.path.exists(xml_voc_dir):
        print("VOC dir {JPEGImages} or {Annotations} is not exist, please check")
        return

    xml_files = [os.path.join(xml_voc_dir, i) for i in os.listdir(xml_voc_dir) if os.path.splitext(i)[-1] == '.xml']
    xml_files = tqdm(xml_files)
    for xml_file in xml_files:
        with open(xml_file) as fid:
            xml_str = fid.read()
        xml = etree.fromstring(xml_str.encode('utf-8'))
        info_dict = parse_xml_to_dict(xml)

        retain_info_dict = parser_retain_info(info_dict, filter_cat_set)
        if len(retain_info_dict['annotation']['object']) <= 0:
            continue

        filename_xml = os.path.basename(xml_file)
        filename_img = retain_info_dict['annotation']['filename']

        ori_img_path = os.path.join(img_voc_dir, filename_img)
        shutil.copy(ori_img_path, img_save_dir)

        save_xml_path = os.path.join(xml_save_dir, filename_xml)
        save_anno_to_xml(retain_info_dict, save_xml_path)

'''
voc_dir: voc 数据集路径
img_voc_dir，xml_voc_dir是标准 voc数据集的图片文件和标签文件路径
save_dir： 筛选后的xml的数据保存路径
filter_set： 需要筛选的类
'''

if __name__ == '__main__':

    voc_dir = "/run/user/1000/gvfs/smb-share:server=192.168.1.197,share=files/sdc/Public_Data_Set/voc2012/VOCdevkit/VOC2012"
    img_voc_dir = os.path.join(voc_dir, "JPEGImages")
    xml_voc_dir = os.path.join(voc_dir, "Annotations")
    save_dir = "/home/ytusdc/Data/voc2012_filter"
    filter_set = set(['bicycle', 'car', 'person', 'motorbike'])
    # get_xml_AllClasses(xml_voc_dir)
    filterXmlFiles(img_voc_dir, xml_voc_dir, save_dir, filter_set)



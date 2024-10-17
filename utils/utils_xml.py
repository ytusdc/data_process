#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-10-16 08:48
Author  : sdc
"""
import os
from lxml import etree, objectify
import xml.etree.ElementTree as ET

def parse_xml_to_dict(xml_tree):
    """
    将xml tree 格式数据，解析成字典形式，参考tensorflow的recursive_parse_xml_to_dict
    Args:
        xml_tree: xml tree obtained by parsing XML file contents using lxml.etree
    Returns:
        Python dictionary holding XML contents.
    """

    if len(xml_tree) == 0:  # 遍历到底层，直接返回tag对应的信息
        return {xml_tree.tag: xml_tree.text}

    result = {}
    for child in xml_tree:
        child_result = parse_xml_to_dict(child)  # 递归遍历标签信息
        if child.tag != 'object':
            result[child.tag] = child_result[child.tag]
        else:
            if child.tag not in result:  # 因为object可能有多个，所以需要放入列表里
                result[child.tag] = []
            result[child.tag].append(child_result[child.tag])
    return {xml_tree.tag: result}

def parser_info_dict(info: dict):
    """
    通过xml解析后得到的字典数据，得到数据的类别 object 和图片的 size
    Args:
        info:
    Returns:
        objects = [object1, objiect2],  object1 =[cls_name, (xmin, ymin, xmax, ymax)]
        size_tuple = (width, height)
    """
    filename = info['annotation']['filename']
    objects = []

    width = int(info['annotation']['size']['width'])
    height = int(info['annotation']['size']['height'])
    # size_tuple = (height, width)
    size_tuple = (width, height)

    if 'object' not in info['annotation']:
        return objects, size_tuple
    for obj in info['annotation']['object']:
        obj_name = obj['name']

        xmin = float(obj['bndbox']['xmin'])
        ymin = float(obj['bndbox']['ymin'])
        xmax = float(obj['bndbox']['xmax'])
        ymax = float(obj['bndbox']['ymax'])
        bbox = (xmin, ymin, xmax, ymax)
        object = [obj_name, bbox]
        objects.append(object)
    return objects, size_tuple

def parse_info_xml(xml_file):
    """
     通过 解析 xml_file 文件， 得到数据的类别 object 和图片的 size
    Args:
        xml_file:
    Returns:
        objects = [object1, objiect2],  object1 =[cls_name, (xmin, ymin, xmax, ymax)]
        size_tuple = (width, height)
    """
    objects = []
    tree = ET.parse(xml_file)
    root = tree.getroot()

    if root.tag != 'annotation':
        raise Exception('pascal voc xml root element should be annotation, rather than {}'.format(root.tag))

    # 提取图片名字
    file_name = root.findtext('filename')
    assert file_name is not None, "filename is not in the file"

    # 初始化图片size
    size = dict()
    size['width'] = None
    size['height'] = None

    # 提取图片 size {width,height,depth}
    size_info = root.findall('size')
    assert size_info is not None, "size is not in the file"
    for subelem in size_info[0]:
        size[subelem.tag] = int(subelem.text)

    # size_tuple = (size['height'], size['width'])
    size_tuple = (size['width'], size['height'])

    # 提取一张图片内所有目标object标注信息
    object_info = root.findall('object')
    if len(object_info) == 0:
        return objects, size_tuple

    # 遍历每个目标的标注信息
    for object in object_info:
        # 提取目标名字
        object_name = object.findtext('name')
        # 初始化标签列表， bndbox voc格式的标注信息
        bndbox_dict = dict()
        bndbox_dict['xmin'] = None
        bndbox_dict['xmax'] = None
        bndbox_dict['ymin'] = None
        bndbox_dict['ymax'] = None
        # 提取box:[xmin,ymin,xmax,ymax]
        bndbox_info = object.findall('bndbox')
        for box in bndbox_info[0]:
            bndbox_dict[box.tag] = int(box.text)

        if bndbox_dict['xmin'] is not None:
            bbox = (bndbox_dict['xmin'], bndbox_dict['xmax'], bndbox_dict['ymin'], bndbox_dict['ymax'])
            obj = [object_name, bbox]
            objects.append(obj)
    return objects, size_tuple

def parse_xml(xml_file, select=True):
    """
    通过两种方式， 解析xml文件，得到数据的类别 object 和图片的 size
    Args:
        xml_file:
        select: 解析数据的不同方式
    Returns:
    """
    if select is True:
        with open(xml_file) as f_r:
            xml_str = f_r.read()
        # xml = etree.fromstring(xml_str)
        xml = etree.fromstring(xml_str.encode('utf-8'))
        info_dict = parse_xml_to_dict(xml)
        return parser_info_dict(info_dict)
    else:
        return parse_info_xml(xml_file)

def save_anno_to_xml(filename, size, objs, save_path):
    """
    Args: 保存信息到 xml 文件
        filename: 图片文件名
        size:
        objs: 保存目标列表: objs = [object1, objiect2],  object1 =[cls_name, [xmin, ymin, xmax, ymax]]
        save_path:
    Returns:
    """
    E = objectify.ElementMaker(annotate=False)
    anno_tree = E.annotation(
        E.folder("DATA"),
        E.filename(filename),
        E.source(
            E.database("The VOC Database"),
            E.annotation("PASCAL VOC"),
            E.image("flickr")
        ),
        E.size(
            E.width(size[1]),
            E.height(size[0]),
            E.depth(size[2])
        ),
        E.segmented(0)
    )
    for obj in objs:
        E2 = objectify.ElementMaker(annotate=False)
        anno_tree2 = E2.object(
            E.name(obj[0]),
            E.pose("Unspecified"),
            E.truncated(0),
            E.difficult(0),
            E.bndbox(
                E.xmin(obj[1][0]),
                E.ymin(obj[1][1]),
                E.xmax(obj[1][2]),
                E.ymax(obj[1][3])
            )
        )
        anno_tree.append(anno_tree2)
    filename_no_ext, ext = os.path.splitext(filename)
    anno_path = os.path.join(save_path, filename_no_ext + ".xml")
    etree.ElementTree(anno_tree).write(anno_path, pretty_print=True)
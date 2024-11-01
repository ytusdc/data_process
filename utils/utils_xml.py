#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-10-16 08:48
Author  : sdc
"""
import os
from lxml import etree, objectify
import xml.etree.ElementTree as ET
from utils import  yamloperate
from tqdm import tqdm

def parse_xmltree_2_dict(xml_tree):
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
        child_result = parse_xmltree_2_dict(child)  # 递归遍历标签信息
        if child.tag != 'object':
            result[child.tag] = child_result[child.tag]
        else:
            if child.tag not in result:  # 因为object可能有多个，所以需要放入列表里
                result[child.tag] = []
            result[child.tag].append(child_result[child.tag])
    return {xml_tree.tag: result}

def parser_info_dict(info: dict):
    """
    通过xml解析后得到的字典数据，得到数据的类别 object 和图片的 size， 允许坐标为float型， 但是一般为 int 型
    Args:
        info:
    Returns:
        objects = [object1, objiect2],  object1 =[cls_name, (xmin, ymin, xmax, ymax)]
            (xmin, ymin, xmax, ymax) 均为字符串类型
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

        # xmin = float(obj['bndbox']['xmin'])
        # ymin = float(obj['bndbox']['ymin'])
        # xmax = float(obj['bndbox']['xmax'])
        # ymax = float(obj['bndbox']['ymax'])
        # 返回坐标为字符串，
        xmin = obj['bndbox']['xmin']
        ymin = obj['bndbox']['ymin']
        xmax = obj['bndbox']['xmax']
        ymax = obj['bndbox']['ymax']
        bbox = (xmin, ymin, xmax, ymax)
        object_one = [obj_name, bbox]
        objects.append(object_one)
    return objects, size_tuple

def parse_xml2dict(xml_file):
    with open(xml_file) as f_r:
        xml_str = f_r.read()
    # xml = etree.fromstring(xml_str)
    xml = etree.fromstring(xml_str.encode('utf-8'))
    info_dict = parse_xmltree_2_dict(xml)
    return info_dict

def parse_xml_by_dict(xml_file):
    xml_info_dict = parse_xmltree_2_dict(xml_file)
    return parser_info_dict(xml_info_dict)

def parse_xml_by_ET(xml_file):
    """
     通过 ET 解析 xml_file 文件， 得到数据的类别 object 和图片的 size， 允许坐标为float型, 但是一般为 int 型
    Args:
        xml_file:
    Returns:
        objects = [object1, objiect2],  object1 =[cls_name, (xmin, ymin, xmax, ymax)]
            (xmin, ymin, xmax, ymax) 均为字符串类型
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
    for obj in object_info:
        # 提取目标名字
        object_name = obj.findtext('name')
        # 初始化标签列表， bndbox voc格式的标注信息
        bndbox_dict = dict()
        bndbox_dict['xmin'] = None
        bndbox_dict['xmax'] = None
        bndbox_dict['ymin'] = None
        bndbox_dict['ymax'] = None
        # 提取box:[xmin,ymin,xmax,ymax]
        bndbox_info = obj.findall('bndbox')
        for box in bndbox_info[0]:
            # bndbox_dict[box.tag] = int(box.text)
            bndbox_dict[box.tag] = box.text  # 返回字符串类型

        if bndbox_dict['xmin'] is not None:
            bbox = (bndbox_dict['xmin'], bndbox_dict['xmax'], bndbox_dict['ymin'], bndbox_dict['ymax'])
            object_one = [object_name, bbox]
            objects.append(object_one)
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
        # with open(xml_file) as f_r:
        #     xml_str = f_r.read()
        # # xml = etree.fromstring(xml_str)
        # xml = etree.fromstring(xml_str.encode('utf-8'))
        # info_dict = parse_xml_to_dict(xml)
        return parse_xml_by_dict(xml_file)
    else:
        return parse_xml_by_ET(xml_file)

def save_anno_to_xml(filename, size, objs, save_path):
    """
    Args: 保存信息到 xml 文件
        filename: 图片文件名
        size: opencv 获取的图片shape
        objs: 保存目标列表: objs = [object1, objiect2],  object1 =[cls_name, [xmin, ymin, xmax, ymax]]
         [xmin, ymin, xmax, ymax] 可以是任意类型 str/int/float 但是推荐为 int
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

def save_info_dict_to_xml(info_dict, save_path):
    """
    保存字典信息到xml
    Args:
        info_dict:
        save_path:

    Returns:

    """
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
    etree.ElementTree(anno_tree).write(save_path, pretty_print=True)


def get_id_class_dict(yaml_file=None, xml_files=None, save_dir=None):
    """
    将类别名字和id建立索引， 返回 {id： 类别名} 字典,
    如果传入 yaml_file 将从 yaml文件中读取索引字典
    如果传入xml_files，save_dir 将从 xml文件中读取所有类别，然后类别名排序后建立索引，
    将索引字典保存到  id_classes.yaml 中
    Args:
        yaml_file:
        xml_files:
        save_dir:
    Returns:
    """

    if yaml_file is not None:
        print('读取 yaml 文件获取 {id：类别名} 索引字典 ')
        id_cls_dict = yamloperate.get_id_cls_dict(yaml_file)
        return id_cls_dict
    elif xml_files is not None and save_dir is not None:
        # 先解析所有xml文件获取所有类别信息 category_set
        category_set = set()
        for xml_file in xml_files:
            objects, _ = parse_xml(xml_file)
            for object in objects:
                object_name = object[0]
                category_set.add(object_name)
        id_cls_dict = dict((k, v) for k, v in enumerate(sorted(category_set)))
        save_yaml_file = os.path.join(save_dir, "id_classes.yaml")
        yamloperate.write_yaml(save_yaml_file, id_cls_dict)
        # class_indices_dict = dict((v, k) for k, v in id_cls_dict.items())
        print("读取 xml 信息，获取 {id：类别名} 索引字典，生成 yaml 文件")
        print(f"生成的 yaml 文件存储在： {save_yaml_file}")
        return id_cls_dict
    else:
        print("如果是从xml文件中获取id-class索引字典，xml_files，save_dir不能为空！")
        return None

'''

xml_file: xml 文件
element: 需要改变的标签
elem_value: 修改后的标签内容
'''

def modify_xml_elem(xml_file, element, elem_value):
    """
    修改特定元素值, 保存并且覆盖原文件
    注意：使用前最好有备份
    Args:
        xml_file: xml 文件
        element:  需要改变的标签
        elem_value: 修改后的标签内容

    Returns:

    """
    tree = ET.parse(xml_file)
    root = tree.getroot()
    # nodes = root.findall('.//filename')
    nodes = root.findall(element)
    for node in nodes:
        node.text = elem_value
    tree.write(xml_file, encoding='utf-8')


# def dict_to_xml(root_tag, d):
#     """
#     将字典转换为XML字符串。
#     参数:
#     - root_tag: XML根标签
#     - d: 字典数据
#     """
#     elem = ET.Element(root_tag)
#     def _dict_to_xml(parent, d):
#         for k, v in d.items():
#             if isinstance(v, dict):
#                 child = ET.SubElement(parent, k)
#                 _dict_to_xml(child, v)
#             else:
#                 ET.SubElement(parent, k).text = str(v)
#
#     _dict_to_xml(elem, d)
#     return ET.tostring(elem, encoding='utf-8').decode('utf-8')


# def parse_cls_info(info: dict):
#     cls_set = set()
#     filename = info['annotation']['filename']
#     if 'object' not in info['annotation']:
#         print(filename)
#         return cls_set
#     for obj in info['annotation']['object']:
#         obj_name = obj['name']
#         cls_set.add(obj_name)
#     return cls_set
#
# def get_xml_AllClasses(voc_xml_dir):
#     xml_files = [os.path.join(voc_xml_dir, i) for i in os.listdir(voc_xml_dir) if os.path.splitext(i)[-1] == '.xml']
#     category_set = set()
#     # 先解析所有xml文件获取所有类别信息 category_set
#     xml_files = tqdm(xml_files)
#     for xml_file in xml_files:
#         with open(xml_file) as fid:
#             xml_str = fid.read()
#         xml = etree.fromstring(xml_str)
#         info_dict = parse_xml_to_dict(xml)
#         classes_set = parse_cls_info(info_dict)
#         category_set.update(classes_set)
#     id_cls_dict = dict((k, v) for k, v in enumerate(sorted(category_set)))
#     class_indices_dict = dict((v, k) for k, v in id_cls_dict.items())
#
#     for key, value in class_indices_dict.items():
#         print(f"{key}:{value}")
#     return class_indices_dict
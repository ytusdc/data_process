#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-10-16 08:48
Author  : sdc
"""
import os
from lxml import etree, objectify


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

def save_anno_to_xml(filename, size, objs, save_path):
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
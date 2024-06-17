import os
import json
import argparse
import sys
import shutil
from lxml import etree
from tqdm import tqdm
from pathlib import Path
import cv2


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

def parseXmlFile(xml_file):

    with open(xml_file) as fid:
        xml_str = fid.read()
    xml = etree.fromstring(xml_str.encode('utf-8'))
    info_dict = parse_xml_to_dict(xml)
    return info_dict

def check_id_equal(images_id_dict, labels_id_dict):

    images_id_set = set(images_id_dict.keys())
    labels_id_set = set(labels_id_dict.keys())
    common_id_set = images_id_set & labels_id_set

    if images_id_set == labels_id_set:
        return common_id_set
    else:
        only_img_id_set = images_id_set - common_id_set
        only_label_id_set = labels_id_set - common_id_set

        if len(only_img_id_set) != 0:
            for img_id in only_img_id_set:
                print(f"image file: {images_id_dict[img_id]} have not correspond xml file")

        if only_label_id_set != 0:
            for label_id in only_label_id_set:
                print(f"xml file: {labels_id_set[label_id]} have not correspond img file")
    return common_id_set

def checkinfo(label_info, labels_class, img_h=None, img_w=None, labels_dir=None):

    # bndbox_ls = label_info['annotation'].['object']
    bndbox_ls = label_info['annotation'].get('object')
    file_name = label_info['annotation']['filename']
    xml_name = str(Path(file_name).stem) + ".xml"
    if bndbox_ls is None:
        print(f"xml file : {labels_dir}/{xml_name}, have not object")
        return True

    for bndbox in bndbox_ls:
        xmax = int(bndbox['bndbox']['xmax'])
        xmin = int(bndbox['bndbox']['xmin'])
        ymax = int(bndbox['bndbox']['ymax'])
        ymin = int(bndbox['bndbox']['ymin'])
        name = bndbox['name']
        if img_h is not None and img_w is not None:
            if xmin < 0 or ymin < 0:
                print(f"xml file : {labels_dir}/{xml_name}, bbox value < 0")
            if xmax > img_w:
                print(f"xml file : {labels_dir}/{xml_name}, bbox xmax value > {img_w}")
            if ymax > img_h:
                print(f"xml file : {labels_dir}/{xml_name}, bbox ymax value > {img_w}")
        if name not in labels_class:
            print(f"xml file : {labels_dir}/{xml_name}, have not lable: {name}")
            return True


def move_file(source_path, destination_path):
    shutil.move(source_path, destination_path)
def beginCheck(images_dir, labels_dir, labels_class, isCheckBoxValue=True, img_type={'.jpg', 'png', '.jpeg'}):

    img_id_dict = {Path(i).stem: os.path.join(images_dir, i) for i in os.listdir(images_dir) if os.path.splitext(i)[-1] in img_type}
    label_id_dict = {Path(i).stem: os.path.join(labels_dir, i) for i in os.listdir(labels_dir) if os.path.splitext(i)[-1] == '.xml'}
    common_id_set = check_id_equal(img_id_dict, label_id_dict)

    height, width = None, None
    for common_id in common_id_set:
        img_file = img_id_dict[common_id]
        xml_file = label_id_dict[common_id]
        try:
            if isCheckBoxValue:
                height, width, _ = cv2.imread(img_file).shape
        except:
            print(f"imge: {img_file}, read error")

        try:
            info_dict = parseXmlFile(xml_file)
            checkinfo(info_dict, labels_class, img_h=height, img_w=width, labels_dir=labels_dir)
            # if re:
            #     move_file(xml_file, "/home/ytusdc/Data/errofile")
            #     move_file(img_file, "/home/ytusdc/Data/errofile")

        except:
            print(f"xml: {xml_file}, parse error")

def main(root_path, label_true):
    for root, dirs, files in os.walk(root_path):
        if "image" in dirs and "xml" in dirs:
            img_dir = os.path.join(root, "image")
            xml_dir = os.path.join(root, "xml")
            # print(f"imgdir= {img_dir}")
            # print(f"xmldir= {xml_dir}")
            beginCheck(img_dir, xml_dir, label_true, isCheckBoxValue=False)

'''
检查数据的类别，标注等信息有没有问题
'''
if __name__ == '__main__':

    labels_true = ['person', 'hat', 'head']  # 真实标签
    root_dir = "/home/ytusdc/Data/数据/人员安全帽"

    # labels_true = ['sleep']  # 真实标签
    # root_dir = '/home/ytusdc/Data/数据/其他类别/睡岗/0201'

    # labels_true = ['export']  # 真实标签
    # root_dir = '/home/ytusdc/Data/数据/其他类别/卸载口'


    # labels_true = ['sleep']  # 真实标签
    # root_dir = '/home/ytusdc/Data/数据/睡岗'

    # labels_true = ['cord']  # 真实标签
    # root_dir = '/home/ytusdc/Data/数据/绞车绳'
    #
    # labels_true = ['truck', 'bus', 'person']  # 真实标签
    # root_dir = '/home/ytusdc/Data/数据/行车(包含人)'


    # labels_true = ['coal', 'roller']  # 真实标签
    # root_dir = '/home/ytusdc/Data/数据/皮带大煤块托辊异物/大煤块托辊'

    # labels_true = ['wood', 'shovel', 'wire', 'box']  # 真实标签
    # root_dir = '/home/ytusdc/Data/数据/皮带大煤块托辊异物/皮带异物'

    main(root_dir, labels_true)

    # beginCheck(voc_images_dir, voc_labels_dir, labels_true, isCheckBoxValue=False)
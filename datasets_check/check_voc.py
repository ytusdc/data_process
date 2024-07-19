import os
import json
import argparse
import sys
import shutil
from lxml import etree
from tqdm import tqdm
from pathlib import Path
import cv2
from utils import modify_elem, get_cls_names_set
from tqdm import tqdm


save_error_files_dir = ""   # 存储出现错误的数据路径， 全局变量
def mkdirs(full_path_dir):
    if not os.path.exists(full_path_dir):
        os.makedirs(full_path_dir)
def move_file(source_path, destination_path):
    shutil.move(source_path, destination_path)

def move_files(img_file, xml_file, move_dir_path):
    mkdirs(move_dir_path)
    move_file(img_file, move_dir_path)
    move_file(xml_file, move_dir_path)

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

'''
 检查 img 和 xml 文件名id是否对应
'''
def check_Img2Xml_Idequal(images_id_dict, labels_id_dict):
    images_id_set = set(images_id_dict.keys())
    labels_id_set = set(labels_id_dict.keys())
    common_id_set = images_id_set & labels_id_set
    if images_id_set == labels_id_set:
        return common_id_set
    else:
        only_img_id_set = images_id_set - common_id_set
        only_label_id_set = labels_id_set - common_id_set

        error_save_file = os.path.join(save_error_files_dir, "have_no_correspond")
        if len(only_img_id_set) != 0:
            mkdirs(error_save_file)
            for img_id in only_img_id_set:
                print(f"image file: {images_id_dict[img_id]} have not correspond xml file")
                move_file(images_id_dict[img_id], error_save_file)

        if only_label_id_set != 0:
            mkdirs(error_save_file)
            for label_id in only_label_id_set:
                print(f"xml file: {labels_id_dict[label_id]} have not correspond img file")
                move_file(labels_id_dict[label_id], error_save_file)
    return common_id_set

def checkinfo(label_info, cls_name_ls, img_file, xml_file, isCheckBoxValue=True):
    # bndbox_ls = label_info['annotation'].['object']
    bndbox_ls = label_info['annotation'].get('object')

    if bndbox_ls is None:
        print(f"xml file : {xml_file}, have not object")
        save_object_error_dir = os.path.join(save_error_files_dir, "xml_have_not_object")
        move_files(img_file, xml_file, save_object_error_dir)
        return True

    img_h, img_w = None, None
    if isCheckBoxValue:
        img_h, img_w, _ = cv2.imread(img_file).shape
    for bndbox in bndbox_ls:
        xmax = int(bndbox['bndbox']['xmax'])
        xmin = int(bndbox['bndbox']['xmin'])
        ymax = int(bndbox['bndbox']['ymax'])
        ymin = int(bndbox['bndbox']['ymin'])
        cls_name = bndbox['name']

        if img_h is not None and img_w is not None:
            is_find_error = False
            if xmin < 0 or ymin < 0:
                print(f"xml file : {xml_file}, bbox value < 0")
                is_find_error = True
            if xmax > img_w:
                print(f"xml file : {xml_file}, bbox xmax value > {img_w}")
                is_find_error = True
            if ymax > img_h:
                print(f"xml file : {xml_file}, bbox ymax value > {img_w}")
                is_find_error = True
            if is_find_error:
                save_cls_error_dir = os.path.join(save_error_files_dir, "img_size_error")
                move_files(img_file, xml_file, save_cls_error_dir)

        if cls_name not in cls_name_ls:
            print(f"xml file : {xml_file}, have not label: {cls_name}")
            save_cls_error_dir = os.path.join(save_error_files_dir, "xml_cls_name_error")
            move_files(img_file, xml_file, save_cls_error_dir)
            return True

'''
检测 xml 文件中记录的 filename， 是否和图片文件名对应,
发现错误的文件, 移动存放在filename_not_equal目录下

ismodify: 如果发现错误时候修改
'''
def check_filename_equal(xml_info, img_file_path, xml_file_path, ismodify=True):
    file_name_in_xml = xml_info['annotation']['filename']
    file_name_img = os.path.basename(img_file_path)
    if file_name_in_xml == file_name_img:
        return True

    if ismodify:
        # 修改xml 中filename 值 为 img 的名字
        modify_elem(xml_file_path, "filename", file_name_img)
        print(f"xml file = {xml_file_path}, in xml name= {file_name_in_xml},  modify filename")
    else:
        error_save_file = os.path.join(save_error_files_dir, "filename_not_equal")
        move_files(img_file_path, xml_file_path, error_save_file)
        print("文件名和xml中的filename不对应")
        print(f"xml file = {xml_file_path}")
        return False

'''
检查, xml中标注的类别名有没有错误
img_dir: 图片文件地址
xml_dir： 对应的 xml 文件地址
cls_name_ls： 类别名列表，eg. ['truck', 'bus', 'person']
isCheckBoxValue: 是否检查图片尺寸
'''
def beginCheck(images_dir, labels_dir, cls_name_ls, isCheckBoxValue=True, img_type={'.jpg', 'png', '.jpeg'}):

    img_id_dict = {Path(i).stem: os.path.join(images_dir, i) for i in os.listdir(images_dir) if os.path.splitext(i)[-1] in img_type}
    label_id_dict = {Path(i).stem: os.path.join(labels_dir, i) for i in os.listdir(labels_dir) if os.path.splitext(i)[-1] == '.xml'}

    global save_error_files_dir
    save_error_files_dir = Path(Path(images_dir).parent, "error")
    common_id_set = check_Img2Xml_Idequal(img_id_dict, label_id_dict)
    for common_id in tqdm(common_id_set):
        img_file = img_id_dict[common_id]
        xml_file = label_id_dict[common_id]

        try:
            xml_info_dict = parseXmlFile(xml_file)
            re = check_filename_equal(xml_info_dict, img_file, xml_file)
            if not re:
                continue
            checkinfo(xml_info_dict, cls_name_ls, img_file, xml_file, isCheckBoxValue=isCheckBoxValue)
        except:
            print(f"xml: {xml_file}, parse error")

'''
遍历文件夹, 一般不需要
'''
def main(root_path, cls_name_ls):
    for root, dirs, files in os.walk(root_path):
        if "image" in dirs and "xml" in dirs:
            img_dir = os.path.join(root, "image")
            xml_dir = os.path.join(root, "xml")
            beginCheck(img_dir, xml_dir, cls_name_ls, isCheckBoxValue=False)

'''
检查数据的类别，标注等信息有没有问题
'''
if __name__ == '__main__':
    # cls_name_ls = ['person', 'hat', 'head']  # 真实标签

    yaml_file = "/home/ytusdc/codes/yolov5/data/coco_belt.yaml"
    yaml_file = "/home/ytusdc/Data/sdc/数据/卸载口/coco_export.yaml"
    # yaml_file = "/home/ytusdc/codes/yolov5/data/coco_hat.yaml"
    cls_name_ls = get_cls_names_set(yaml_file)

    # voc_images_dir = "/home/ytusdc/filename_not_equal"
    #
    # voc_labels_dir = "/home/ytusdc/filename_not_equal"
    # voc_images_dir = "/home/ytusdc/Data/filename_not_equal"
    # voc_labels_dir = "/home/ytusdc/Data/filename_not_equal"
    # beginCheck(voc_images_dir, voc_labels_dir, cls_name_ls, isCheckBoxValue=False)

    root_dir = "/home/ytusdc/Data/数据_原始/皮带大煤块托辊异物"
    root_dir = "/home/ytusdc/Data/sdc/数据/卸载口"
    main(root_dir, cls_name_ls)
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.append("..")

import os
import argparse
import shutil
from lxml import etree
from pathlib import Path
import cv2
from tqdm import tqdm

from utils import *

def mkdirs(full_path_dir):
    if not os.path.exists(full_path_dir):
        os.makedirs(full_path_dir)
def move_file(source_path, destination_path):
    shutil.move(source_path, destination_path)

def move_files(img_file, xml_file, move_dir_path):
    mkdirs(move_dir_path)
    move_file(img_file, move_dir_path)
    move_file(xml_file, move_dir_path)

class CheckVocInfo:
    def __init__(self, images_dir: str, labels_dir: str, save_error_dir: str, yaml_file=None):
        """
        Args:
            images_dir:
            labels_dir:
            save_error_dir: 保存错误数据路径
            yaml_file:
        """
        self.images_dir = images_dir
        self.labels_dir = labels_dir
        self.save_error_dir = save_error_dir   # 存储出现错误的数据路径
        self.yaml_file = yaml_file

    '''
     检查 img 和 xml 文件是否一一对应，
    '''
    def check_Img2Xml_Idequal(self, images_dir, labels_dir):

        images_id_path_dict = common_fun.get_id_path_dict(images_dir)
        labels_id_path_dict = common_fun.get_id_path_dict(labels_dir, suffix='.xml')
        images_id_set = set(images_id_path_dict.keys())
        labels_id_set = set(labels_id_path_dict.keys())
        common_id_set = images_id_set & labels_id_set
        if images_id_set == labels_id_set:
            print("img 和 label 文件一一对应")
            return common_id_set
        else:
            only_img_id_set = images_id_set - common_id_set
            only_label_id_set = labels_id_set - common_id_set

            error_save_file = os.path.join(self.save_error_dir, "have_no_correspond")
            if len(only_img_id_set) != 0:
                mkdirs(error_save_file)
                for img_id in only_img_id_set:
                    print(f"image file: {images_id_path_dict[img_id]} have not correspond xml file")
                    move_file(images_id_path_dict[img_id], error_save_file)

            if len(only_label_id_set) != 0:
                mkdirs(error_save_file)
                for label_id in only_label_id_set:
                    print(f"xml file: {labels_id_path_dict[label_id]} have not correspond img file")
                    move_file(labels_id_path_dict[label_id], error_save_file)

    '''
    检测 xml 文件中记录的 filename， 是否和图片文件名对应,
    ismodify: 如果发现错误时候修改, 默认修改,     
    如果发现错误的文件不修改, 则移动存放在filename_not_equal目录下
    '''
    def check_filename_equal(self, images_dir, labels_dir, ismodify=True):
        images_id_path_dict = common_fun.get_id_path_dict(images_dir)
        labels_id_path_dict = common_fun.get_id_path_dict(labels_dir, suffix='.xml')
        images_id_set = set(images_id_path_dict.keys())
        labels_id_set = set(labels_id_path_dict.keys())
        common_id_set = images_id_set & labels_id_set

        for common_id in tqdm(common_id_set):
            img_file_path = images_id_path_dict[common_id]
            xml_file_path = labels_id_path_dict[common_id]
            xml_info = utils_xml_opt.parse_xml2dict(xml_file_path)
            file_name_in_xml = xml_info['annotation']['filename']
            file_name_img = os.path.basename(img_file_path)
            if file_name_in_xml == file_name_img:
                continue
            else:
                if ismodify:
                    # 修改xml 中filename 值 为 img 的名字
                    utils_xml_opt.modify_xml_elem(xml_file_path, "filename", file_name_img)
                    print(f"xml file = {xml_file_path}, in xml name= {file_name_in_xml},  modify filename")
                else:
                    error_save_file = os.path.join(self.save_error_dir, "filename_not_equal")
                    move_files(img_file_path, xml_file_path, error_save_file)
                    print("文件名和xml中的filename不对应")
                    print(f"xml file = {xml_file_path}")

    def checkinfo(self, images_dir, labels_dir, yaml_file=None):
        """
        Args:
            labels_dir:
            label_info:
            yaml_file:

        Returns:
        1、检查 类别名是否跟yaml_file中相同
        2、检查 图片读取是否有问题
        3、检查 xml 中是否有标注目标
        4、检查 bbox标注是否越界
        """

        cls_name_set = set()
        if yaml_file is not None:
            cls_name_set = get_id_cls_dict(yaml_file).values()
            if len(cls_name_set) == 0:
                print(f"yaml 文件中没有读取到类别信息： {yaml_file}, ")
                return

        images_id_path_dict = common_fun.get_id_path_dict(images_dir)
        label_id_path_dict = common_fun.get_id_path_dict(labels_dir, suffix='.xml')
        images_id_set = set(images_id_path_dict.keys())
        labels_id_set = set(label_id_path_dict.keys())
        common_id_set = images_id_set & labels_id_set

        for id in common_id_set:
            img_file = images_id_path_dict[id]
            xml_file = label_id_path_dict[id]
            label_info = utils_xml_opt.parse_xml2dict(xml_file)

            bndbox_ls = label_info['annotation'].get('object')

            # 图像中没有标注目标
            if bndbox_ls is None:
                save_object_error_dir = os.path.join(self.save_error_dir, "xml_have_not_object")
                if not os.path.exists(save_object_error_dir):
                    os.makedirs(save_object_error_dir)
                print(f"xml file : {xml_file}, have not object")
                move_files(img_file, xml_file, save_object_error_dir)
                continue

            img = cv2.imread(img_file)
            # 可能图片文件损坏，单独存储
            if img is None:
                save_img_none_error_dir = os.path.join(self.save_error_dir, "img_None_error")
                move_files(img_file, xml_file, save_img_none_error_dir)
                continue

            img_h, img_w, _ = img.shape

            for bndbox in bndbox_ls:
                xmax = int(bndbox['bndbox']['xmax'])
                xmin = int(bndbox['bndbox']['xmin'])
                ymax = int(bndbox['bndbox']['ymax'])
                ymin = int(bndbox['bndbox']['ymin'])
                cls_name = bndbox['name']

                # 检查 voc 标注是否超越界限
                if xmin < 0 or ymin < 0 or xmax > img_w or ymax > img_h:
                    print(f"xml file : {xml_file}, bbox 越界")
                    save_cls_error_dir = os.path.join(self.save_error_dir, "img_size_error")
                    move_files(img_file, xml_file, save_cls_error_dir)

                # yaml_file 不为None时， 检测 voc 中类别名是否正确
                if yaml_file is not None and cls_name not in cls_name_set:
                    print(f"xml file : {xml_file}, have not label: {cls_name}")
                    save_cls_error_dir = os.path.join(self.save_error_dir, "xml_cls_name_error")
                    move_files(img_file, xml_file, save_cls_error_dir)

    def begin_check(self):
        self.check_Img2Xml_Idequal(self.images_dir, self.labels_dir)
        self.check_filename_equal(self.images_dir, self.labels_dir)
        self.checkinfo(self.images_dir, self.labels_dir, self.yaml_file)

'''
检查, xml中标注的类别名有没有错误
img_dir: 图片文件地址
xml_dir： 对应的 xml 文件地址
'''
'''
检查数据的类别，标注等信息有没有问题
'''
if __name__ == '__main__':

    '''
        images_dir = "path/to/image"
        labels_dir = "path/to/xml"
        save_error_dir = "path/to/save_error"
        yaml_file = "path/to/yamfile"  或者 None
    '''

    images_dir = "/home/ytusdc/Data/吸烟/image"
    labels_dir = "/home/ytusdc/Data/吸烟/xml"
    save_error_dir = "/home/ytusdc/Data/吸烟/error"
    yaml_file = None
    yaml_file = "/home/ytusdc/Data/id_classes.yaml"
    checkvoc_cls = CheckVocInfo(images_dir, labels_dir, save_error_dir, yaml_file)
    checkvoc_cls.begin_check()
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-10-29 14:22
Author  : sdc
"""

import os
import sys
from pathlib import Path
import argparse
import shutil
import xml.etree.ElementTree as ET

def update_category(xml_file, save_xml_dir, rename_category_map_dict):
    # 解析XML文件
    tree = ET.parse(xml_file)
    root = tree.getroot()

    ismodify = False
    # 更新类别标签
    for obj in root.findall('object'):
        name = obj.find('name').text
        if name in rename_category_map_dict.keys():
            obj.find('name').text = rename_category_map_dict[name]
            ismodify = True

    # 保存修改后的XML文件
    if ismodify:
        rename_xml_file_name = Path(save_xml_dir, Path(xml_file).name)
        tree.write(rename_xml_file_name, encoding='utf-8', xml_declaration=True)
        print(f"{os.path.basename(xml_file)} modify label")
    else:
        shutil.copy(xml_file, save_xml_dir)


# 类别名修改后，不修改源文件，而是存储到新建的文件夹中，放置污染原始标签文件
def process_directory(voc_dir, rename_category_map):
    merge_xml_name = "xml_modify_class"
    save_rename_dir = Path(Path(voc_dir).parent, merge_xml_name)
    if not Path(save_rename_dir).exists():
        Path(save_rename_dir).mkdir(parents=True, exist_ok=True)
    else:
        if len(os.listdir(save_rename_dir)) > 0:
            print(f"文件夹：{save_rename_dir}，不为空，程序退出")
            return

    # 遍历目录中的所有XML文件
    for filename in os.listdir(voc_dir):
        if filename.endswith('.xml'):
            xml_file = os.path.join(voc_dir, filename)
            update_category(xml_file, save_rename_dir, rename_category_map)

'''
voc 不同类别合并, 或者 类别改名
'''
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--voc-dir', type=str, default=None, help='voc 标注文件xml路径')
    opt = parser.parse_args()

    input_args = sys.argv[1:]  # 第一个参数是脚本名本身
    if len(input_args) > 0:
        if len(input_args) / 2 != 1:
            print(f"必须传入一个参数，请检查输入")
            sys.exit(-1)
        voc_label_dir = opt.voc_dir
    else:
        voc_label_dir = "path/to/voc_xml"    # 指定VOC数据集的标注文件目录s

    voc_label_dir = "/home/ytusdc/Data/Data_car_1223/xml_未合并/xml_1000_原始未合并/xml"
    # 定义 需要合并的类别映射
    # key: 原有类别名，
    # value：更改后的类别名
    category_map = {
        'pickup': 'car',
        'bus2': 'car',
    }
    # 调用函数处理目录中的所有XML文件
    process_directory(voc_label_dir, category_map)

if __name__ == '__main__':
    main()

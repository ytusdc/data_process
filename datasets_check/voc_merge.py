#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-10-29 14:22
Author  : sdc
"""

import os
import sys
import argparse
import xml.etree.ElementTree as ET

def update_category(xml_file, merge_category_map):
    # 解析XML文件
    tree = ET.parse(xml_file)
    root = tree.getroot()

    ismodify = False
    # 更新类别标签
    for obj in root.findall('object'):
        name = obj.find('name').text
        if name in merge_category_map:
            obj.find('name').text = merge_category_map[name]
            ismodify = True

    # 保存修改后的XML文件
    if ismodify:
        tree.write(xml_file, encoding='utf-8', xml_declaration=True)
        print(f"{os.path.basename(xml_file)} modify label")

def process_directory(directory, merge_category_map):
    # 遍历目录中的所有XML文件
    for filename in os.listdir(directory):
        if filename.endswith('.xml'):
            xml_file = os.path.join(directory, filename)
            update_category(xml_file, merge_category_map)

'''
voc 不同类别合并, / 类别改名
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
        voc_label_dir = "path/to/voc_xml"    # 指定VOC数据集的标注文件目录
        voc_label_dir = "/home/ytusdc/Data/原始数据/车辆数据/车辆/xml"    # 指定VOC数据集的标注文件目录


    # 定义 需要合并的类别映射
    category_map = {
        'pickup': 'car',
        'bus2': 'car',
    }

    # 调用函数处理目录中的所有XML文件
    process_directory(voc_label_dir, category_map)

if __name__ == '__main__':
    main()

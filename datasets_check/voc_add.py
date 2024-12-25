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
from utils import *
def process_directory(xml_file_path, voc_dir):
    """
    Args:
        xml_file_path: 需要单独增加的标注信息
        voc_dir: voc 文件夹路径
    Returns:
    """
    add_xml_name = "xml_add_class"
    save_dir = Path(Path(voc_dir).parent, add_xml_name)
    if not Path(save_dir).exists():
        Path(save_dir).mkdir(parents=True, exist_ok=True)
    else:
        if len(os.listdir(save_dir)) > 0:
            print(f"文件夹：{save_dir}，不为空，程序退出")
            return

    add_info_dict = utils_xml_opt.parse_xml2dict(xml_file_path)
    add_class_ls = add_info_dict["annotation"]["object"]

    # 遍历目录中的所有XML文件
    for filename in sorted(os.listdir(voc_dir)):
        if filename.endswith('.xml'):
            xml_file = os.path.join(voc_dir, filename)
            xml_info_dict = utils_xml_opt.parse_xml2dict(xml_file)
            xml_info_dict["annotation"]["object"].extend(add_class_ls)
            save_xml_file = Path(save_dir, Path(xml_file).name)
            utils_xml_opt.save_info_dict_to_xml(xml_info_dict, str(save_xml_file))


'''
统一在xml中增加相同的标注
'''
def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('-v', '--voc-dir', type=str, default=None, help='voc 标注文件xml路径')
    # opt = parser.parse_args()
    #
    # input_args = sys.argv[1:]  # 第一个参数是脚本名本身
    # if len(input_args) > 0:
    #     if len(input_args) / 2 != 1:
    #         print(f"必须传入一个参数，请检查输入")
    #         sys.exit(-1)
    #     voc_label_dir = opt.voc_dir
    # else:
    #     voc_label_dir = "path/to/voc_xml"    # 指定VOC数据集的标注文件目录s

    file_path = "/home/ytusdc/Data/Data_yiwu_exact/000000.xml"
    voc_dir = "/home/ytusdc/Data/Data_yiwu_exact/xml_coal"

    process_directory(file_path, voc_dir)

if __name__ == '__main__':
    main()

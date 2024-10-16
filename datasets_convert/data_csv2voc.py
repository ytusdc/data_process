#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-08-21 10:07
Author  : sdc
"""
"""
csv 文件数据 转 xml 数据
"""

import sys
sys.path.append("..")

import os
import argparse
from tqdm import tqdm

from utils import *

def csv2json(csv_file, xml_save_dir):
    assert os.path.exists(csv_file), "csv file :{} dose not exists".format(csv_file)

    if not operate_dir.mkdirs(xml_save_dir):
        print(f"{xml_save_dir} : 文件夹不为空或者文件夹创建失败，请检查, 退出函数！")
        return

    with open(csv_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    lines_data = lines[1:]   # 一般第一行是标题，所以从第二行取数据（根据具体情况变动）
    filename_ls = list()     # 获取 文件名列表， 文件名可能会有重复,需要进一步处理
    for line in lines_data:
        row = line.strip().split(',')
        filename = row[1]    # 文件名需要根据 csv 具体的位置确定
        filename_ls.append(filename)

    filename_index_dict = common_fun.find_duplicate_elem_indices(filename_ls)
    for filename, index_ls in tqdm(filename_index_dict.items()):
        objects = []

        # 每个参数具体所在位置， 需要根据自己的csv文件调整
        for index in index_ls:
            row_data = lines_data[index].strip().split(',')
            width = int(row_data[8])
            height = int(row_data[7])
            channel = int(row_data[9])
            label = row_data[2]
            category_name = str(label)
            xmin = int(row_data[3])
            ymin = int(row_data[4])
            xmax = int(row_data[5])
            ymax = int(row_data[6])
            bbox = [xmin, ymin, xmax, ymax]
            obj = [category_name, bbox]

            objects.append(obj)
        shape = [height, width, channel]
        utils_xml_opt.save_anno_to_xml(filename, shape, objects, xml_save_dir)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--img-dir', type=str, default=None, help='图片文件路径')
    parser.add_argument('-s', '--save-dir', type=str, default=None, help='存储标签文件路径, voc格式')
    opt = parser.parse_args()

    input_args = sys.argv[1:]  # 第一个参数是脚本名本身
    if len(input_args) > 0:
        if len(input_args) / 2 != 2:
            print(f"必须传入两个参数，请检查输入, 退出脚本！")
            sys.exit(-1)
        img_dir = opt.img_dir  # 图片源文件地址
        xml_dir = opt.save_dir  # 对应标签源文件
    else:
        img_dir = "path/to/file.csv"
        xml_dir = "path/to/xml_dir"
    csv2json(img_dir, xml_dir)


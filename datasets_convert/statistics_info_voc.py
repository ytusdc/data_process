#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-10-17 08:32
Author  : sdc
"""
import sys
sys.path.append("..")

import os
import argparse
from collections import defaultdict
import matplotlib.pyplot as plt
import datetime
from tqdm import tqdm
from operator import itemgetter

from collections import OrderedDict

from utils import *

"""
统计信息，并且绘制柱形图，然后输出结果
"""
def plot_statistics_info(category_num_dict):

    # 按值降序排列
    sorted_by_value_dict = OrderedDict(sorted(category_num_dict.items(), key=lambda item: item[1], reverse=True))

    print("-------各类别信息如下-----------")
    box_num = 0
    for category_name, num in sorted_by_value_dict.items():
        print(f"{category_name}:{num}")
        box_num += num
    print("*****************************")
    print(f"category nums: {len(sorted_by_value_dict.keys())}")
    print(f"bbox nums: {box_num}")
    print("------------------------------")
    # 绘制每种类别个数柱状图
    plt.bar(range(len(sorted_by_value_dict)), sorted_by_value_dict.values(), align='center')
    # 将横坐标0,1,2,3,4替换为相应的类别名称
    plt.xticks(range(len(sorted_by_value_dict)), sorted_by_value_dict.keys(), rotation=90)
    # 在柱状图上添加数值标签
    for index, (cls, num) in enumerate(sorted_by_value_dict.items()):
        plt.text(x=index, y=num, s=str(num), ha='center')
        # print(f"{cls}:{num}")

    # 设置x坐标
    plt.xlabel('image class')
    # 设置y坐标
    plt.ylabel('number of images')
    # 设置柱状图的标题
    plt.title('class distribution')
    # 保存柱状图
    now = datetime.datetime.now()
    time_str = now.strftime('%Y%m%d-%H%M%S')
    plt.savefig(f"class_distribution_{time_str}.png")
    # plt.show()
    print(f"统计信息可视化图片：class_distribution_{time_str}.png")


def statistics_info(xml_dir):
    assert os.path.exists(xml_dir), "ERROR {} does not exists".format(xml_dir)

    # 类别名和类别数量
    category_num_dict = defaultdict(int)
    xml_files_ls = common_fun.get_filepath_ls(xml_dir, suffix=".xml")

    for xml_file in tqdm(xml_files_ls):
        objects, _ = utils_xml_opt.parse_xml(xml_file, select=True)
        for obj in objects:
            object_name = obj[0]
            category_num_dict[object_name] += 1

    plot_statistics_info(category_num_dict)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--voc-dir', type=str, default=None, help='voc 文件路径')
    opt = parser.parse_args()

    input_args = sys.argv[1:]  # 第一个参数是脚本名本身
    if len(input_args) > 0:
        if opt.voc_dir is None:
            print("voc 文件路径不能为空, 退出脚本！")
            sys.exit(-1)
        voc_xml_dir = opt.voc_dir
    else:
        voc_xml_dir = "/path/to/xml"

    statistics_info(voc_xml_dir)

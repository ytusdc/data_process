#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-10-10 15:55
Author  : sdc
收集的不同数据集有时会出现命名相同或者命名很接近的情况，为了方便区分，加一个前缀
"""
import os.path
import utils.common as common_fun
import shutil




if __name__ == '__main__':

    img_dir = "/home/ytusdc/Downloads/烟雾+火焰/可用/fire+smoke/新增火焰烟雾V2/images"
    label_dir = "/home/ytusdc/Downloads/烟雾+火焰/可用/fire+smoke/新增火焰烟雾V2/xml"

    new_img_dir = "/home/ytusdc/Downloads/烟雾+火焰/可用/fire+smoke/新增火焰烟雾V2/new_images"
    new_label_dir = "/home/ytusdc/Downloads/烟雾+火焰/可用/fire+smoke/新增火焰烟雾V2/new_xml"

    id_img_dict = common_fun.get_filter_file(img_dir)
    id_label_dict = common_fun.get_filter_file(label_dir, file_suffix=".xml")

    id_img_set = id_img_dict.keys()
    id_label_set = id_label_dict.keys()

    prefix = 'v2_'

    if id_img_set != id_label_set:
        print("图片文件和标签文件不能一一对应，请核对")
    else:
        for id in id_img_set:
            img_file = id_img_dict[id]
            label_file = id_label_dict[id]
            new_id = prefix + id

            img_suffix = os.path.splitext(img_file)[-1]
            label_suffix = os.path.splitext(label_file)[-1]

            new_img_file = os.path.join(new_img_dir, new_id + img_suffix)
            new_label_file = os.path.join(new_label_dir, new_id + label_suffix)
            shutil.copy(img_file, new_img_file)
            shutil.copy(label_file, new_label_file)




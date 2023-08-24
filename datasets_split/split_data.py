#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from pathlib import Path
import shutil
from sklearn.model_selection import train_test_split


'''
data_dir: 文件路径
file_suffix： 文件后缀 None/str/[str1,str2,..]
'''
def get_filter_file(data_dir, file_suffix=None):
    file_ls = []
    # 过滤掉 ‘.’开头的隐藏文件, 有的情况下会出现，大部分情况不会，以防万一
    filter_file_ls = os.listdir(data_dir)
    for i in range(len(filter_file_ls) - 1, -1, -1):  # for i in range(0, num_list.__len__())[::-1]
        if filter_file_ls[i].startswith('.'):
            filter_file_ls.pop(i)

    if file_suffix is None:
        file_ls = filter_file_ls
    # 根据文件后缀过滤
    elif isinstance(file_suffix, str):
        file_ls = list(filter(lambda x: x.endswith(file_suffix), filter_file_ls))
    elif isinstance(file_suffix, list):
        file_ls = [file_name for file_name in filter_file_ls
                  if os.path.splitext(file_name)[-1] in file_suffix]
        # for suffix in file_suffix:
        #     child_ls = list(filter(lambda x: x.endswith(suffix), os.listdir(data_dir)))
        #     file_ls.extend(child_ls)

    sorted_file_ls = sorted(file_ls)  # 排序，保证各平台顺序一致
    return sorted_file_ls

def get_id_filename_dict(data_dir):
    # 过滤掉 ‘.’开头的隐藏文件, 有的情况下会出现，大部分情况不会，以防万一
    filter_file_ls = os.listdir(data_dir)
    for i in range(len(filter_file_ls) - 1, -1, -1):  # for i in range(0, num_list.__len__())[::-1]
        if filter_file_ls[i].startswith('.'):
            filter_file_ls.pop(i)
    id_name_dict = {os.path.splitext(name)[0]: name for name in filter_file_ls}
    return id_name_dict

'''
ori_img_dir: 需要划分的数据集中存放图片的路径
ori_label_dir: 需要划分的数据集中存放标签的路径
des_img_dir： 划分后的图片存放路径
des_label_dir： 划分后的标签存放路径
split_percent_dict,  数据集划分比例字典，比例之和必须为1，否则报错， 可以划分两个或者三个数据集
img_suffix: 文件后缀 None/str/[str1,str2,..]  如：[‘.jpg’, '.png']
random_seed = 100 随机种子保证可重复性
'''

def split_data(ori_img_dir, ori_label_dir, des_img_dir, des_label_dir, split_percent_dict, img_suffix=None, random_seed=100):

      # 保证随机结果可复现

    split_name_ls = []
    split_percent_ls = []
    split_img_ls = []

    percent_sum = 0
    for split_name, percent in split_percent_dict.items():
        split_name_ls.append(split_name)
        split_percent_ls.append(percent)
    for percent in split_percent_ls:
        percent_sum += float(percent)

    assert percent_sum == 1, "sum percent is not equal 1, please make sure the sum percent is 1."
    # if percent_sum != 1:
    #     print(f"sum percent is not equal 1, please make sure the sum percent is 1.")
    #     return

    imgs_ls = get_filter_file(ori_img_dir, img_suffix)

    if len(split_per_dict) == 2:
        X_train, X_test = train_test_split(imgs_ls, test_size=split_percent_ls[-1], random_state=random_seed)
        # X_train, X_test, Y_train, Y_test  = train_test_split(imgs_ls, imgs_ls, test_size=split_percent_ls[-1], random_state=100)
        split_img_ls.append(X_train)
        split_img_ls.append(X_test)
    elif len(split_per_dict) == 3:
        split_testval = split_percent_ls[-1] + split_percent_ls[-2]
        X_train, X_testval = train_test_split(imgs_ls, test_size=split_testval, random_state=random_seed)
        new_perent = split_percent_ls[-2] / split_testval
        new_train, new_test = train_test_split(X_testval, test_size=new_perent, random_state=random_seed)
        split_img_ls.append(X_train)
        split_img_ls.append(new_train)
        split_img_ls.append(new_test)
    else:
        print(f"split percent len is error")
        return

    for split_dir_name, img_ls in zip(split_name_ls, split_img_ls):

        target_img_path = Path(des_img_dir, split_dir_name)
        if not Path(target_img_path).exists():
            Path(target_img_path).mkdir(parents=True, exist_ok=True)
        target_label_path = Path(des_label_dir, split_dir_name)
        if not Path(target_label_path).exists():
            Path(target_label_path).mkdir(parents=True, exist_ok=True)

        id_img_dict = get_id_filename_dict(ori_img_dir)
        id_label_dict = get_id_filename_dict(ori_label_dir)

        imgs_id_ls = list(map(lambda x: os.path.splitext(x)[0], img_ls))
        for id in imgs_id_ls:
            src_img_file = Path(ori_img_dir, id_img_dict[id])
            src_label_file = Path(ori_label_dir, id_label_dict[id])
            shutil.copy(src_img_file, target_img_path)
            shutil.copy(src_label_file, target_label_path)

if __name__ == '__main__':
    split_per_dict = {
        "train": 0.8,
        "test2": 0.1,
        "val": 0.1, }

    # split_per_dict = {
    #     "train": 0.8,
    #     "test": 0.2
    #     }


    ori_img_dir = "/home/cv/datasets/data_ori/images"      # 图片源文件地址
    ori_label_dir = "/home/cv/datasets/data_ori/labels"    # 标签源文件

    des_img_dir = "/home/cv/datasets/data_split/images"    # 图片目标地址
    des_label_dir = "/home/cv/datasets/data_split/labels"  #  标签目标地址

    split_data(ori_img_dir, ori_label_dir, des_img_dir, des_label_dir, split_per_dict)




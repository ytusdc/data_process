#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
sys.path.append("..")

from pathlib import Path
import shutil
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import argparse

from utils import *
"""
默认数据集中 image和label文件夹文件没有问题，在不考虑后缀名的前提下，
只获取id 和对应文件名没有问题
"""
def get_id_filename_dict(data_dir):
    # 过滤掉 ‘.’开头的隐藏文件, 有的情况下会出现，大部分情况不会，以防万一
    filter_file_ls = os.listdir(data_dir)
    for i in range(len(filter_file_ls) - 1, -1, -1):  # for i in range(0, num_list.__len__())[::-1]
        if filter_file_ls[i].startswith('.'):
            filter_file_ls.pop(i)
    id_name_dict = {os.path.splitext(name)[0]: name for name in filter_file_ls}
    return id_name_dict

'''
找到没有对应的标签或者图片，单独保存，
'''
def compare_img_label(img_dir, label_dir):
    id_img_dict = common_fun.get_id_path_dict(img_dir)
    id_label_dict = common_fun.get_id_path_dict(label_dir, suffix=['.txt', '.xml'])

    img_id_set = set(id_img_dict.keys())
    label_id_set = set(id_label_dict.keys())

    if img_id_set == label_id_set:
        print("图片文件和标签文件可以一一对应")
        return True

    remain_img_id_set = set()
    remain_label_id_set = set()

    is_subset = label_id_set.issubset(img_id_set)
    is_superset = label_id_set.issuperset(img_id_set)
    if is_subset:
        # img_id_set 包含 label_id_set, 标签文件是否是图片文件的子集
        remain_img_id_set.update(img_id_set - label_id_set)
    elif is_superset:
        # label_id_set 包含 img_id_set, 标签文件是否是图片文件的超集
        remain_label_id_set.update(label_id_set - img_id_set)
    else:
        # label_id_set 和 img_id_set 中各自有不同元素，这种情况比较少
        remain_img_id_set.update(img_id_set - label_id_set)
        remain_label_id_set.update(label_id_set - img_id_set)

    save_remain_img_dir = Path(Path(img_dir).parent, "remain_img")
    save_remain_label_dir = Path(Path(label_dir).parent, "remain_label")
    if len(remain_img_id_set) > 0:
        re = operate_dir.mkdirs(save_remain_img_dir)
        if not re:
            print(f"Path: {save_remain_img_dir} , is not empty, please check")
            return False
        else:
            print(f"找到没有标签对应的图片，存放在: {save_remain_img_dir}")
    if len(remain_label_id_set) > 0:
        re = operate_dir.mkdirs(save_remain_label_dir)
        if not re:
            print(f"Path: {save_remain_label_dir} , is not empty, please check")
            return False
        else:
            print(f"找到没有图片对应的标签，存放在: {save_remain_label_dir}")

    for img_id in remain_img_id_set:
        img_path = id_img_dict[img_id]
        shutil.move(img_path, save_remain_img_dir)

    for label_id in remain_label_id_set:
        label_path = id_label_dict[label_id]
        shutil.move(label_path, save_remain_label_dir)

'''
ori_img_dir: 需要划分的数据集中存放图片的路径
ori_label_dir: 需要划分的数据集中存放标签的路径
des_img_dir： 划分后的图片存放路径
des_label_dir： 划分后的标签存放路径
split_percent_dict,  数据集划分比例字典，比例之和必须为1，否则报错， 可以划分两个或者三个数据集
img_suffix: 文件后缀 None/str/[str1,str2,..]  如：[‘.jpg’, '.png']
random_seed = 100 随机种子保证可重复性, 保证随机结果可复现
'''
def split_data(ori_img_dir,
               ori_label_dir,
               des_img_dir,
               des_label_dir,
               split_percent_dict,
               img_suffix=None,
               random_seed=100):

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

    imgs_ls = common_fun.get_filename_ls(ori_img_dir, suffix=img_suffix)

    if len(split_percent_dict) == 2:
        X_train, X_test = train_test_split(imgs_ls, test_size=split_percent_ls[-1], random_state=random_seed)
        # X_train, X_test, Y_train, Y_test  = train_test_split(imgs_ls, imgs_ls, test_size=split_percent_ls[-1], random_state=100)
        split_img_ls.append(X_train)
        split_img_ls.append(X_test)
    elif len(split_percent_dict) == 3:
        # 分两次划分
        split_testval = split_percent_ls[-1] + split_percent_ls[-2]
        X_train, X_testval = train_test_split(imgs_ls, test_size=split_testval, random_state=random_seed)
        new_perent = split_percent_ls[-2] / split_testval
        new_X_train, new_X_test = train_test_split(X_testval, test_size=new_perent, random_state=random_seed)
        split_img_ls.append(X_train)
        split_img_ls.append(new_X_train)
        split_img_ls.append(new_X_test)
    else:
        print(f"split percent len is error")
        return

    for split_dir_name, img_ls in zip(split_name_ls, split_img_ls):

        # 前面的步骤已经判断了文件夹是否为空，这里不用再判断了
        target_img_path = Path(des_img_dir, split_dir_name)
        if not Path(target_img_path).exists():
            Path(target_img_path).mkdir(parents=True, exist_ok=True)
        target_label_path = Path(des_label_dir, split_dir_name)
        if not Path(target_label_path).exists():
            Path(target_label_path).mkdir(parents=True, exist_ok=True)

        id_img_dict = get_id_filename_dict(ori_img_dir)
        id_label_dict = get_id_filename_dict(ori_label_dir)

        imgs_id_ls = list(map(lambda x: os.path.splitext(x)[0], img_ls))

        for id in tqdm(imgs_id_ls, desc=split_dir_name + " split process"):
            # print(id)
            src_img_file = Path(ori_img_dir, id_img_dict[id])
            src_label_file = Path(ori_label_dir, id_label_dict[id])
            shutil.copy(src_img_file, target_img_path)
            shutil.copy(src_label_file, target_label_path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--img-dir', type=str, default=None, help='图片文件路径')
    parser.add_argument('-l', '--label-dir', type=str, default=None, help='对应标签文件路径（yolo/voc）格式')
    parser.add_argument('-d', '--des-dir', type=str, default=None, help='划分后数据集存储路径')
    opt = parser.parse_args()

    # 划分 三个数据集
    split_per_dict = {
        "train": 0.8,
        "test": 0.1,
        "val": 0.1, }

    # 划分两个数据集
    # split_per_dict = {
    #     "train": 0.8,
    #     "test": 0.2
    #     }

    input_args = sys.argv[1:]  # 第一个参数是脚本名本身
    if len(input_args) > 0:
        if len(input_args) / 2 != 3:
            print(f"必须传入三个参数，请检查输入")
            sys.exit(-1)
        if opt.img_dir is None or opt.label_dir is None or opt.des_dir is None:
            print(f"参数不能为 None")
            sys.exit(-1)
        ori_img_dir = opt.img_dir        # 图片源文件地址
        ori_label_dir = opt.label_dir    # 对应标签源文件
        des_dir = opt.des_dir            # 划分后数据集保存位置
    else:
        ori_img_dir = "path/to/img"      # 图片源文件地址
        ori_label_dir = "path/to/label"  # 对应标签源文件
        des_dir = "path/to/save"         # 划分后数据集保存位置

    # 划分后数据集 自动生成 images， labels 文件夹，根据需要自己修改
    des_img_dir = os.path.join(des_dir, "images")    # 图片目存储标地址
    des_label_dir = os.path.join(des_dir, "labels")  # 标签目标存储地址
    ret_0 = operate_dir.mkdirs(des_img_dir)
    ret_1 = operate_dir.mkdirs(des_label_dir)

    if not ret_0:
        print(f"{des_img_dir}, 不为空，请检查")
        return

    if not ret_1:
        print(f"{des_label_dir}, 不为空，请检查")
        return

    compare_img_label(ori_img_dir, ori_label_dir)
    split_data(ori_img_dir, ori_label_dir, des_img_dir, des_label_dir, split_per_dict)

if __name__ == '__main__':
    main()





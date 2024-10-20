#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from pathlib import Path
import shutil
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import argparse


'''
data_dir: 文件路径
file_suffix： 文件后缀 None/str/[str1,str2,..]
['jpg', 'png', 'jpeg']

'''
# def get_filter_file(data_dir, file_suffix=None):
def get_filter_file(data_dir, file_suffix=['.jpg', '.png', '.jpeg']):
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

    if img_suffix is None:
        imgs_ls = get_filter_file(ori_img_dir)
    else:
        imgs_ls = get_filter_file(ori_img_dir, img_suffix)

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
        ori_img_dir = opt.img_dir  # 图片源文件地址
        ori_label_dir = opt.label_dir  # 对应标签源文件
        des_dir = opt.des_dir  # 划分后数据集保存位置
    else:
        ori_img_dir = ""  # 图片源文件地址
        ori_label_dir = ""  # 对应标签源文件
        des_dir = ""  # 划分后数据集保存位置

    # 划分后数据集 自动生成 images， labels 文件夹，根据需要自己修改
    des_img_dir = os.path.join(des_dir, "images")    # 图片目存储标地址
    des_label_dir = os.path.join(des_dir, "labels")  # 标签目标存储地址
    split_data(ori_img_dir, ori_label_dir, des_img_dir, des_label_dir, split_per_dict)

if __name__ == '__main__':
    main()





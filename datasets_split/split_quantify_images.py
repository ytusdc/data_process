#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-10-21 18:00
Author  : sdc
"""

'''
随机获取量化用的图片
'''
import os
from sklearn.model_selection import train_test_split
from pathlib import Path
import shutil
# 图片后缀
global_img_suffix = ['.jpg', '.png', '.jpeg', '.bmp']
def find_files_by_extension(directory, suffix=None):
    if suffix is None:
        suffix = global_img_suffix  # 如果 suffix 为None， 则默认使用 图片过滤
    files_list = []
    for root, dirs, files in os.walk(directory):
        new_list = []
        if isinstance(suffix, str):
            new_list = [os.path.join(root, x) for x in files if x.lower().endswith(suffix)]
        elif isinstance(suffix, list):
            new_list = [os.path.join(root, x) for x in files if
                       os.path.splitext(x.lower())[-1] in suffix]
        files_list.extend(new_list)
    return files_list

"""
random_seed = 100 随机种子保证可重复性, 保证随机结果可复现
"""
def get_quantify_images(files_ls, img_num=500, random_seed=100):

    files_sorted_ls = sorted(files_ls)  # 保证顺序相同
    X_train, _ = train_test_split(files_sorted_ls, train_size=img_num, random_state=random_seed)
    return X_train

if __name__ == '__main__':
    directory_path = '/home/ytusdc/Data/Data_car_1223/images/train'
    save_dir = "/home/ytusdc/测试数据/random"

    files_ls = find_files_by_extension(directory_path)
    random_files_ls = get_quantify_images(files_ls)

    Path(save_dir).mkdir(parents=True, exist_ok=True)
    for file_path in random_files_ls:
        shutil.copy(file_path, save_dir)
    pass
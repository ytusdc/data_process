#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-10-09 15:35
Author  : sdc
"""
import os
import sys
from fileinput import filename
from pathlib import Path
"""
获取文件夹下相关列表或者字典
"""

# 图片后缀
global_img_stuffix = ['.jpg', '.png', '.jpeg', '.bmp']

"""
过滤特定类型，获取文件名列表， 默认获取图片文件列表
suffix： 文件后缀 None/str/[str1,str2,..]
"""
def get_filename_ls(data_dir, suffix=None):
    if suffix is None:
        suffix = global_img_stuffix  # 如果 suffix 为None， 则默认使用 图片过滤

    # 过滤掉 ‘.’开头的隐藏文件, 有的情况下会出现，大部分情况不会，以防万一
    filter_file_ls = os.listdir(data_dir)
    for i in range(len(filter_file_ls) - 1, -1, -1):  # for i in range(0, num_list.__len__())[::-1]
        if filter_file_ls[i].startswith('.'):
            filter_file_ls.pop(i)
    file_ls = []
    if isinstance(suffix, str):
        file_ls = list(filter(lambda x: x.lower().endswith(suffix), filter_file_ls))
        # file_ls = [x for x in filter_file_ls if x.lower().endswith(suffix)]
    elif isinstance(suffix, list):
        # file_ls = list(filter(lambda x: os.path.splitext(x.lower())[-1] in suffix, filter_file_ls))
        file_ls = [x for x in filter_file_ls if os.path.splitext(x.lower())[-1] in suffix]
    return sorted(file_ls)  # 排序， 不同平台保持顺序一致

"""
过滤特定类型，获取文件全路径列表， 默认获取图片文件列表
"""
def get_filepath_ls(data_dir, suffix=None):
    if suffix is None:
        suffix = global_img_stuffix  # 如果 suffix 为None， 则默认使用 图片过滤

    # 过滤掉 ‘.’开头的隐藏文件, 有的情况下会出现，大部分情况不会，以防万一
    filter_file_ls = os.listdir(data_dir)
    for i in range(len(filter_file_ls) - 1, -1, -1):  # for i in range(0, num_list.__len__())[::-1]
        if filter_file_ls[i].startswith('.'):
            filter_file_ls.pop(i)
    file_ls = []
    if isinstance(suffix, str):
        file_ls = [os.path.join(data_dir, x) for x in filter_file_ls if x.lower().endswith(suffix)]
    elif isinstance(suffix, list):
        file_ls = [os.path.join(data_dir, x) for x in filter_file_ls if os.path.splitext(x.lower())[-1] in suffix]
    return sorted(file_ls)  # 排序， 不同平台保持顺序一致

"""
获取文件 id： fullpath, 字典， id 不包含后缀
前提是文件名命名没有相同的，因为id不包含后缀，如 1.jpg 和 1.png 是不同的文件但是id相同
"""
def get_id_path_dict(data_dir, suffix=None):
    if suffix is None:
        suffix = global_img_stuffix  # 如果 suffix 为None， 则默认使用 图片过滤
    file_ls = []
    # 过滤掉 ‘.’开头的隐藏文件, 有的情况下会出现，大部分情况不会，以防万一
    filter_file_ls = os.listdir(data_dir)
    # filter_file_ls =  [os.path.join(data_dir, i) for i in os.listdir(data_dir)]
    for i in range(len(filter_file_ls) - 1, -1, -1):  # for i in range(0, num_list.__len__())[::-1]
        if filter_file_ls[i].startswith('.'):
            filter_file_ls.pop(i)

    # 不过滤后缀扩展名，得到目录下所有文件list
    if suffix is None:
        file_ls = filter_file_ls
    # 根据文件后缀过滤
    elif isinstance(suffix, str):
        file_ls = list(filter(lambda x: x.lower().endswith(suffix), filter_file_ls))
    elif isinstance(suffix, list):
        file_ls = [file_name for file_name in filter_file_ls
                   if os.path.splitext(file_name.lower())[-1] in suffix]

    # img_id_dict = {Path(i).stem: os.path.join(imgs_dir, i) for i in os.listdir(imgs_dir) if os.path.splitext(i)[-1] in suffix}
    # label_id_dict = {Path(i).stem: os.path.join(annos_dir, i) for i in os.listdir(annos_dir) if os.path.splitext(i)[-1]=='.txt'}

    id_filepath_dict = {}
    for filename in sorted(file_ls):    # 排序，保证各平台顺序一致
        name_no_stffix = os.path.splitext(filename)[0]
        if name_no_stffix in set(id_filepath_dict.keys()):
            print(f"发现重复id,请检查，程序退出：{name_no_stffix}")
            sys.exit(-1)
        else:
            id_filepath_dict[name_no_stffix] = os.path.join(data_dir, filename)
    return id_filepath_dict

def get_id_filename_dict(data_dir, suffix=None):
    if suffix is None:
        suffix = global_img_stuffix  # 如果 suffix 为None， 则默认使用 图片过滤
    filter_filename_ls  = get_filename_ls(data_dir, suffix=suffix)
    id_name_dict = {os.path.splitext(name)[0]: name for name in filter_filename_ls}
    return id_name_dict

"""
获取图片 文件名： fullpath, 字典， 防止出现重复的id，
"""
def get_filename_path_dict(data_dir, suffix=None):
    if suffix is None:
        suffix = global_img_stuffix  # 如果 suffix 为None， 则默认使用 图片过滤
    file_ls = []
    # 过滤掉 ‘.’开头的隐藏文件, 有的情况下会出现，大部分情况不会，以防万一
    filter_file_ls = os.listdir(data_dir)
    for i in range(len(filter_file_ls) - 1, -1, -1):  # for i in range(0, num_list.__len__())[::-1]
        if filter_file_ls[i].startswith('.'):
            filter_file_ls.pop(i)

    # 不过滤，得到目录下所有文件list
    if suffix is None:
        file_ls = filter_file_ls
    # 根据文件后缀过滤
    elif isinstance(suffix, str):
        file_ls = list(filter(lambda x: x.endswith(suffix), filter_file_ls))
    elif isinstance(suffix, list):
        file_ls = [file_name for file_name in filter_file_ls
                  if os.path.splitext(file_name)[-1] in suffix]

    filename_filepath_dict = {}
    for file_name in sorted(file_ls):
        filename_filepath_dict[file_name] = os.path.join(data_dir, file_name)
    return filename_filepath_dict

def find_duplicate_elem(arry_list):
    """
    查找list中，相同的元素
    """
    # arry_list = sorted(arry_list)
    from collections import Counter
    # 方法1
    def find_duplicates_with_counter(input_list):
        count = Counter(input_list)
        duplicates = [item for item, cnt in count.items() if cnt > 1]
        return duplicates
    #方法2
    def find_duplicates_with_list_comprehension(input_list):
        return list(set([x for x in input_list if input_list.count(x) > 1]))
    duplicates_list = find_duplicates_with_counter(arry_list)
    # duplicates = find_duplicates_with_list_comprehension(arry_list)
    return duplicates_list


def find_duplicate_elem_indices(lst):
    """
    基于字典的方法, 获取每个元素的所有索引位置
    """
    # 创建一个空字典来存储元素及其索引
    index_dict = {}
    # 遍历列表，同时获取元素及其索引
    for index, element in enumerate(lst):
        # 如果元素已经在字典中，则添加新的索引到对应的值列表中
        if element in index_dict:
            index_dict[element].append(index)
        else:
            # 如果元素不在字典中，则创建一个新的键值对
            index_dict[element] = [index]
    return index_dict

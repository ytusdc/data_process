#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-10-09 15:35
Author  : sdc
"""
import os
"""
获取图片 id： fullpath, 字典
前提是文件名命名没有相同的，因为id不包含后缀，如 1.jpg 和 1.png 是不同的文件但是id相同
"""
def get_id_path_dict(data_dir, file_suffix=['.jpg', '.png', '.jpeg', '.bmp']):
    file_ls = []
    # 过滤掉 ‘.’开头的隐藏文件, 有的情况下会出现，大部分情况不会，以防万一
    filter_file_ls = os.listdir(data_dir)
    # filter_file_ls =  [os.path.join(data_dir, i) for i in os.listdir(data_dir)]
    for i in range(len(filter_file_ls) - 1, -1, -1):  # for i in range(0, num_list.__len__())[::-1]
        if filter_file_ls[i].startswith('.'):
            filter_file_ls.pop(i)

    # 不过滤，得到目录下所有文件list
    if file_suffix is None:
        file_ls = filter_file_ls
    # 根据文件后缀过滤
    elif isinstance(file_suffix, str):
        file_ls = list(filter(lambda x: x.lower().endswith(file_suffix), filter_file_ls))
    elif isinstance(file_suffix, list):
        file_ls = [file_name for file_name in filter_file_ls
                  if os.path.splitext(file_name.lower())[-1] in file_suffix]
        # for suffix in file_suffix:
        #     child_ls = list(filter(lambda x: x.endswith(suffix), os.listdir(data_dir)))
        #     file_ls.extend(child_ls)

    id_filepath_dict = {}
    for file_name in sorted(file_ls):    # 排序，保证各平台顺序一致
        name = os.path.splitext(file_name)[0]
        id_filepath_dict[name] = os.path.join(data_dir, file_name)

    return id_filepath_dict

"""
获取图片 文件名： fullpath, 字典， 防止出现重复的id，
"""
def get_filename_path_dict(data_dir, file_suffix=['.jpg', '.png', '.jpeg']):
    file_ls = []
    # 过滤掉 ‘.’开头的隐藏文件, 有的情况下会出现，大部分情况不会，以防万一
    filter_file_ls = os.listdir(data_dir)
    for i in range(len(filter_file_ls) - 1, -1, -1):  # for i in range(0, num_list.__len__())[::-1]
        if filter_file_ls[i].startswith('.'):
            filter_file_ls.pop(i)

    # 不过滤，得到目录下所有文件list
    if file_suffix is None:
        file_ls = filter_file_ls
    # 根据文件后缀过滤
    elif isinstance(file_suffix, str):
        file_ls = list(filter(lambda x: x.endswith(file_suffix), filter_file_ls))
    elif isinstance(file_suffix, list):
        file_ls = [file_name for file_name in filter_file_ls
                  if os.path.splitext(file_name)[-1] in file_suffix]

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
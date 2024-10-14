#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-10-12 10:56
Author  : sdc
"""

import uuid
import os



def get_filter_file(data_dir, file_suffix=['.jpg', '.png', '.jpeg', '.bmp']):
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

    sorted_file_ls = sorted(file_ls)  # 排序，保证各平台顺序一致

    id_filepath_dict = {}
    for file_name in sorted_file_ls:
        # name = os.path.splitext(file_name)[0]
        # id_filepath_dict[name] = os.path.join(data_dir, file_name)
        id_filepath_dict[file_name] = os.path.join(data_dir, file_name)

    return id_filepath_dict


img_dir = "/home/ytusdc/Pictures/动火/label"

id_path_dict = get_filter_file(img_dir)

for file_name, path in id_path_dict.items():
    name, stuff = os.path.splitext(file_name)
    parent_dir = os.path.dirname(path)
    if len(name) < 10:
        uuid_value = uuid.uuid4()
        new_name = str(uuid_value) + stuff
        new_path = os.path.join(parent_dir, new_name)
        mv_str = f"mv {path} {new_path}"
        os.system(mv_str)






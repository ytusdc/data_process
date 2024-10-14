#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-10-14 16:58
Author  : sdc
"""
"""
文件命名规范化
1、长度太短的用uuid重命名
2、后缀统一改成小写
"""
import uuid
import os
import shutil

def rename_uuid(filepath_ls, min_len=15):
    """
    判断文件名长度是否小于 min_len， 文件名太短可能容易重复，重新生成 uuid name
    min_len: 最小长度
    """
    for file_path in filepath_ls:
        file_name = os.path.basename(file_path)
        name, stuff = os.path.splitext(file_name)
        parent_dir = os.path.dirname(file_path)
        if len(name) < min_len:
            uuid_value = uuid.uuid4()
            new_name = str(uuid_value) + stuff
            new_path = os.path.join(parent_dir, new_name)
            shutil.move(file_path, new_path)

            # mv_str = f"mv {file_path} {new_path}"
            # os.system(mv_str)

def lower_suffix(data_dir):
    """
    文件后缀名，都改成小写
    """
    # 过滤掉 ‘.’开头的隐藏文件, 有的情况下会出现，大部分情况不会，以防万一
    filter_file_ls = os.listdir(data_dir)
    for i in range(len(filter_file_ls) - 1, -1, -1):  # for i in range(0, num_list.__len__())[::-1]
        if filter_file_ls[i].startswith('.'):
            filter_file_ls.pop(i)
    for file_name in filter_file_ls:
        name, stuff = os.path.splitext(file_name)
        if stuff != stuff.lower():
            ori_path = os.path.join(data_dir, file_name)
            new_path = os.path.join(data_dir, name + stuff.lower())
            shutil.move(ori_path, new_path)

def main(data_dir):
    rename_uuid(data_dir)
    lower_suffix(data_dir)

if __name__ == '__main__':
    file_folder = ""
    main(file_folder)
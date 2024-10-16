#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-10-16 10:56
Author  : sdc
"""
import os


def is_empty_dir(path_dir):
    entries = os.listdir(path_dir)
    # 如果目录中有任何条目，则该目录不为空
    return len(entries) == 0

def mkdirs(full_path_dir):
    if not os.path.exists(full_path_dir):
        os.makedirs(full_path_dir)
        return True   # 文件夹创建成功
    else:
        if not is_empty_dir(full_path_dir):
            return False    # 文件夹不为空
        else:
            return True     # 文件夹为空


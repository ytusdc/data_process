#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-08-13 16:32
Author  : sdc
"""
import os
def mkdirs(full_path_dir):
    if not os.path.exists(full_path_dir):
        os.makedirs(full_path_dir)
        return True
    else:
        print(f"{full_path_dir} is exist, please modify save folder")
        return False
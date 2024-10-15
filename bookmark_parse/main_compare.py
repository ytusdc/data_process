#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-10-15 14:18
Author  : sdc
"""
import compare_by_url
import compare_by_dir

"""
只找出新增项，其他的暂时不考虑
"""
if __name__ == '__main__':
    old_html_file = "/home/ytusdc/Documents/favorites_9_25_24_111.html"
    new_html_file = '/home/ytusdc/Documents/favorites_10_11_24.html'
    labelname = "网文html"

    # labelname下逐个文件夹， 比较其中的url异同
    compare_by_dir.main(old_html_file, new_html_file, labelname)

    print("******************************************")
    # labelname 下 所有的url 比较异同
    compare_by_url.main(old_html_file, new_html_file, labelname)
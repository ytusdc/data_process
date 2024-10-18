#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-10-15 14:14
Author  : sdc
"""
import parse_bookmark_html_to_json as parse_html_fun
from utils import print_with_style_and_color

"""
url作为key比较不同
"""

def process_json_data(json_data, url_name_dict, labelname=None):
    """
    Args:
        json_data: html 解析后的 json数据
        url_name_dict: url 作为key，是为了防止 name 名字重复的情况
        labelname: 需要查找的标签文件夹名， 如果 labelname=None， 则查找整个书签文件
    Returns:
    """
    """
    递归处理多层级的 JSON 字典数据， 获取每个链接 name 和 url
    """
    if labelname is not None:
        name = json_data["name"]
        if name == labelname:
            for child in json_data["children"]:
                process_json_data(child, url_name_dict)
        else:
            if "children" in json_data.keys():
                for child in json_data["children"]:
                    process_json_data(child, url_name_dict, labelname)
    else:
        if "url" in json_data.keys():
            url_name = json_data["name"]
            url = json_data["url"]
            if url in url_name_dict.values():
                print(f"重复的书签： {url_name}, {url}")
            else:
                url_name_dict[url] = url_name
        elif "children" in json_data.keys():
            for child in json_data["children"]:
                process_json_data(child, url_name_dict)

def get_url_name_dict(html_file, label_name):
    """
    获取 url->name 对应的字典
    """
    bookmark_json =  parse_html_fun.html_2_json(html_file)
    result_dict = dict()
    process_json_data(bookmark_json, result_dict, labelname=label_name)
    # print(f"result_dict = {len(result_dict)}")
    return result_dict

def main(bookmark_file_old, bookmark_file_new, label_name):
    """
    比较两个 html书签 文件中不同的项目(新增)， 基于 url 进行比较
    Args:
        bookmark_file_old:
        bookmark_file_new:
        label_name: 书签文件中的指定比对的目录
    Returns:
    """
    old_url_name_dict = get_url_name_dict(bookmark_file_old, label_name)
    new_url_name_dict = get_url_name_dict(bookmark_file_new, label_name)
    old_url_set = old_url_name_dict.keys()
    new_url_set = new_url_name_dict.keys()
    diff_url_set = new_url_set - old_url_set

    for url in diff_url_set:
        name = new_url_name_dict[url]
        print(f"{name} : {url}")

    print(f"************************************")
    print_with_style_and_color(f"总共找到不同项 {len(diff_url_set)} 个", color='red', style='bold')

if __name__ == '__main__':
    old_html_file = "/home/ytusdc/Documents/favorites_9_25_24_111.html"
    # old_html_file = '/home/ytusdc/Documents/favorites_10_11_24.html'
    new_html_file = '/home/ytusdc/Documents/favorites_10_11_24.html'

    labelname = "网文html"
    # labelname = None
    main(old_html_file, new_html_file, labelname)
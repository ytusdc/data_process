#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-10-11 11:21
Author  : sdc
"""
import parse_bookmark_html_to_json as prase_html_fun
from utils import print_with_style_and_color

"""
获取目录， 比价相同目录下的url异同
"""

"""
获取 json_data 中 labelname （子目录名）的信息
"""
def process_json_data(json_data, url_name_dict, labelname=None):
    if labelname is not None:
        name = json_data["name"]
        if name == labelname:
            url_name_dict["name"] = labelname
            url_name_dict["children"] = json_data["children"]
        else:
            if "children" in json_data.keys():
                for child in json_data["children"]:
                    process_json_data(child, url_name_dict, labelname)

"""
只解析有一层结构的目录，多级结构报错，退出
"""
def process_dict(data_dict, label_name):
    dir_node_dict = {}
    root_node_dict = {}
    for child in data_dict["children"]:
        if "children" in child.keys() and "url" not in child.keys():
            dir_name = child['name']
            node_list = child['children']
            url_name_dict = {}
            try:
                for node in node_list:
                    url = node['url']
                    url_name = node['name']
                    url_name_dict[url] = url_name
            except:
                print(f" {dir_name}: 该目录下包含多层目录结构， 暂时只支持一层目录结构")
                exit(-1)
            dir_node_dict[dir_name] = url_name_dict
        else:
            url = child["url"]
            url_name = child["name"]
            root_node_dict[url] = url_name
    dir_node_dict[label_name] = root_node_dict
    return dir_node_dict

def find_url_add(base_url_dict, compare_url_dict):
    """
    按目录结构输出，比较得到不同 url， 方便查看
    以新的书签数据为基准，比较新增的url（基准标签中有，被比较标签没有的url），
    不考虑被比较标签有，基准标签没有的情况
    Args:
        base_url_dict: 基准标签（新标签）
        compare_url_dict: 被比较标签（旧标签）
    Returns:
    """
    for base_key in base_url_dict.keys():
        if base_key in compare_url_dict.keys():
            base_url_set = set(base_url_dict[base_key])
            compare_url_set = set(compare_url_dict[base_key])
            diff_url_set = base_url_set - compare_url_set
            if len(diff_url_set) <= 0:
                continue
            print_with_style_and_color(f"{base_key}  {'' * 10}", color='red', style='bold')
            for url in diff_url_set:
                url_name = base_url_dict[base_key][url]
                print_with_style_and_color(f"{'-' * 5}{url_name} : {url}")
        else:
            if len(base_url_dict[base_key]) <= 0:
                continue
            print_with_style_and_color(f"{base_key}  {'' * 10}", color='red', style='bold')
            for url, url_name in base_url_dict[base_key].items():
                print_with_style_and_color(f"{'-' * 5}{url_name} : {url}")

def get_contents_dict(bookmark_file, label_name):
    bookmark_json =  prase_html_fun.html_2_json(bookmark_file)
    result_dict = dict()
    process_json_data(bookmark_json, result_dict, labelname=label_name)
    contents_dict = process_dict(result_dict, label_name)
    return contents_dict

def main(bookmark_file_old, bookmark_file_new, label_name):
    """
    比较两个 html书签 文件中不同的项目， 基于 url 进行比较
    Args:
        bookmark_file_old:
        bookmark_file_new:
        label_name: 书签文件中的指定比对的目录
    Returns:
    """

    new_dict = get_contents_dict(bookmark_file_new, label_name)
    old_dict = get_contents_dict(bookmark_file_old, label_name)
    find_url_add(new_dict, old_dict)

if __name__ == '__main__':
    old_html_file = "/home/ytusdc/Documents/favorites_9_25_24_111.html"
    new_html_file = '/home/ytusdc/Documents/favorites_10_11_24.html'
    labelname = "网文html"
    main(old_html_file, new_html_file, labelname)
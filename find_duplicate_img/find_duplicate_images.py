#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-10-10 08:41
Author  : sdc
通过图片哈希值，查找重复的图片文件
"""
import os

from PIL import Image
import imagehash
from utils import common as common_fun
# import utils.common as common_fun
import shutil

def get_image_hash(image_path):
    """ 计算图片的哈希值 """
    try:
        with Image.open(image_path) as img:
            return imagehash.average_hash(img)
    except Exception as e:
        print(f"无法打开图片 {image_path}: {e}")
        return None

def get_hash_img_dict(image_dir):
    """
    获取文件夹下图片的 hash：图片路径 对应字典，如果文件件下有相同的图片，则退出
    需要先解决掉自身目录下相同的图片问题
    """
    hash_image_dict = {}
    id_img_dict = common_fun.get_id_path_dict(image_dir)
    for img_file in id_img_dict.values():
        hash_value = get_image_hash(img_file)
        if hash_value in set(hash_image_dict.keys()):
            print("该目录下发现相同的img 文件，请检查")
            print(f"image: {img_file}")
            print(f"duplicate image: {hash_image_dict[hash_value]}")
            exit(-1)
        hash_image_dict[hash_value] = img_file
    return hash_image_dict

def get_img_hash_dict(image_dir):
    """
    获取文件夹下图片的 图片路径 : hash 对应字典，字典不会出现相同key的情况
    """
    image_hash_dict = {}
    filename_img_dict = common_fun.get_filename_path_dict(image_dir)
    for img_file in filename_img_dict.values():
        hash_value = get_image_hash(img_file)
        image_hash_dict[img_file] = hash_value
    return image_hash_dict

"""
比较查找两个文件夹下，相同图片， 如果本目录下有相同的图片，则报错，需要先保证本目录下没有相同图片
"""
def find_duplicate_img(ori_img_dir, compare_img_dir, duplicate_dir):
    """
    Args:
        duplicate_dir: 相同的文件移动到指定目录
    """
    duplicates_ls = []
    ori_img_hash_dict = get_hash_img_dict(ori_img_dir)
    compare_img_hash_dict = get_hash_img_dict(compare_img_dir)

    ori_hash_set = set(ori_img_hash_dict.keys())
    compare_hash_set = set(compare_img_hash_dict.keys())
    common_hash_set = ori_hash_set & compare_hash_set
    for common_hash in list(common_hash_set):
        ori_img_file = ori_img_hash_dict[common_hash]
        compare_img_file = compare_img_hash_dict[common_hash]
        duplicates_ls.append((ori_img_file, compare_img_file))

    for index, dup_tuple in enumerate(duplicates_ls):
        print(f"重复图片: {dup_tuple[0]} 和 {dup_tuple[1]}")
        prefix = f"{index}_duplicate_"
        _, filename_1 = os.path.split(dup_tuple[0])
        _, filename_2 = os.path.split(dup_tuple[1])

        if filename_1 == filename_2:
            move_path_1 =  os.path.join(duplicate_dir, prefix + '0_' + filename_1)
            move_path_2 =  os.path.join(duplicate_dir, prefix + '1_' + filename_2)
            shutil.move(dup_tuple[0], move_path_1)
            shutil.move(dup_tuple[1], move_path_2)
        else:
            shutil.move(dup_tuple[0], duplicate_dir)
            shutil.move(dup_tuple[1], duplicate_dir)

"""
查找自身目录下相同图片, 相同的图片加入前缀 num_duplicate_, 移动到指定目录
"""
def find_self_duplicate_img(img_dir, duplicate_dir):
    """
    Args:
        img_dir:
        duplicate_dir: 相同的文件移动到指定目录
    """
    image_hash_dict = get_img_hash_dict(img_dir)
    hash_list = list(image_hash_dict.values())
    duplicate_hash_list = common_fun.find_duplicate_elem(hash_list)
    duplicate_hash_set = set(duplicate_hash_list)

    if len(duplicate_hash_set) > 0:
        print(f"发现图片重复的哈希值 {len(duplicate_hash_set) } 个")
    else:
        print(f"没有重复文件，可能多张相同hash值的图片")

    for img_file, hash_value in image_hash_dict.items():
        if hash_value in duplicate_hash_set:
            index = duplicate_hash_list.index(hash_value)
            prefix = f"{index}_duplicate_"
            dirname, filename = os.path.split(img_file)
            move_path = os.path.join(duplicate_dir, prefix + filename)
            shutil.move(img_file, move_path)

"""
遍历查找当前目录下所有重复的文件, 查找当前目录及其子目录中的重复图片
"""
def find_duplicate_images(directory):
    """ 查找目录中所有图片的哈希值，并找出重复的图片 """
    image_hashes = {}
    duplicates = []
    for root, _, files in os.walk(directory):
        for file in sorted(files):
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                file_path = os.path.join(root, file)
                hash_value = get_image_hash(file_path)
                if hash_value is not None:
                    if hash_value in set(image_hashes.keys()):
                        # duplicates.append((file_path, image_hashes[hash_value]))
                        duplicates.append((image_hashes[hash_value], file_path))
                    else:
                        image_hashes[hash_value] = file_path
    return duplicates

"""
把带有 _duplicate_ 前缀的图片，重新还原回来原来的的图片名
"""
def rename_duplicate_img(duplicate_dir):
    id_img_dict = common_fun.get_id_path_dict(duplicate_dir)

    common_str = "_duplicate_"
    for img_file in id_img_dict.values():
        dirname, filename = os.path.split(img_file)
        index = filename.index(common_str)
        ori_name = filename[index + len(common_str):]
        new_img_file = os.path.join(dirname, ori_name)
        shutil.move(img_file, new_img_file)

if __name__ == '__main__':
    ori_dir = "/home/ytusdc/Pictures/动火/test"
    compare_dir = "/home/ytusdc/Pictures/动火/label"
    dupli_dir = "/home/ytusdc/Pictures/动火/dupli"
    find_self_duplicate_img(compare_dir, dupli_dir)
    # rename_duplicate_img(dupli_dir)




import os
import json
import argparse
import sys
from lxml import etree
from tqdm import tqdm
from pathlib import Path
import cv2
from utils import modify_elem, get_cls_names_set
from tqdm import tqdm
import numpy as np
import utils

save_error_files_dir = ""   # 存储出现错误的数据路径， 全局变量

'''
 检查 img 和 标签 文件名id是否对应
 返回 共同标签的 id set
'''
def check_Img2Label_Idequal(images_id_dict, labels_id_dict):
    images_id_set = set(images_id_dict.keys())
    labels_id_set = set(labels_id_dict.keys())
    common_id_set = images_id_set & labels_id_set
    if images_id_set == labels_id_set:
        return common_id_set
    else:
        only_img_id_set = images_id_set - common_id_set
        only_label_id_set = labels_id_set - common_id_set

        error_save_file = os.path.join(save_error_files_dir, "have_no_correspond")
        if len(only_img_id_set) != 0:
            utils.mkdirs(error_save_file)
            for img_id in only_img_id_set:
                print(f"image file: {images_id_dict[img_id]} have not correspond json file")
                utils.move_file(images_id_dict[img_id], error_save_file)

        if only_label_id_set != 0:
            utils.mkdirs(error_save_file)
            for label_id in only_label_id_set:
                print(f"xml file: {labels_id_dict[label_id]} have not correspond img file")
                utils.move_file(labels_id_dict[label_id], error_save_file)
    return common_id_set

def checkinfo(cls_name_ls, img_file, json_file):
    h, w, labels_ls, points_ls = parse_json(json_file)

    if len(labels_ls) == 0 or len(points_ls) == 0:
        print(f"json file : {json_file}, have not object")
        save_object_error_dir = os.path.join(save_error_files_dir, "xml_have_not_object")
        utils.move_files(img_file, json_file, save_object_error_dir)
        return True

    for label, points in zip(labels_ls, points_ls):
        if len(points) < 3:
            print(f"Error: must be at least 3 pairs: {json_file} points lens= {len(points)}")

        if label not in cls_name_ls:
            print(f"xml file : {json_file}, have not label: {label}")
            save_cls_error_dir = os.path.join(save_error_files_dir, "xml_cls_name_error")
            utils.move_files(img_file, json_file, save_cls_error_dir)
            return True

        points_np = np.array(points, dtype=np.float64).reshape(-1, 2)
        np_w = points_np[:, 0] < w
        np_h = points_np[:, 1] < h

        tmp_1 = np.where(np_w == False)[0]
        tmp_2 = np.where(np_h == False)[0]

        if len(tmp_1) > 0 or len(tmp_2) > 0:
            print(f"points value exceed width or height")
            save_exceed_error_dir = os.path.join(save_error_files_dir, "value_exceed_error")
            utils.move_files(img_file, json_file, save_exceed_error_dir)

'''
检查, xml中标注的类别名有没有错误
img_dir: 图片文件地址
xml_dir： 对应的 xml 文件地址
cls_name_ls： 类别名列表，eg. ['truck', 'bus', 'person']
isCheckBoxValue: 是否检查图片尺寸
'''
def beginCheck(images_dir, labels_dir, yaml_file, img_type={'.jpg', 'png', '.jpeg'}):
    cls_name_ls = get_cls_names_set(yaml_file)

    cls_name_ls = ["coal"]

    img_id_dict = {Path(i).stem: os.path.join(images_dir, i) for i in os.listdir(images_dir) if os.path.splitext(i)[-1] in img_type}
    label_id_dict = {Path(i).stem: os.path.join(labels_dir, i) for i in os.listdir(labels_dir) if os.path.splitext(i)[-1] == '.json'}

    global save_error_files_dir
    save_error_files_dir = Path(Path(images_dir).parent, "error")
    common_id_set = check_Img2Label_Idequal(img_id_dict, label_id_dict)
    for common_id in tqdm(common_id_set):
        img_file = img_id_dict[common_id]
        json_file = label_id_dict[common_id]
        try:
            checkinfo(cls_name_ls, img_file, json_file)
        except:
            print(f"xml: {json_file}, parse error")

'''
label_ls:   标签类别列表
points_ls： 标签对应的点
'''
def parse_json(json_file):
    label_ls = []
    points_ls = []
    with open(json_file, "r") as file_r:
        json_dict = json.load(file_r)
        h, w = json_dict['imageHeight'], json_dict['imageWidth']
        for shape_dict in json_dict['shapes']:
            label = shape_dict['label']
            label_ls.append(label)
            points = shape_dict['points']
            points_ls.append(points)

    # result = list(zip(label_ls, points_ls))
    return h, w, label_ls, points_ls








'''
遍历文件夹, 一般不需要
'''



'''
检查数据的类别，标注等信息有没有问题
'''
if __name__ == '__main__':


    yaml_file = "/home/ytusdc/project/data_process/datasets_convert/yaml/coco_hat_truck.yaml"
    img_dir = "/home/ytusdc/Data/sdc/煤流检测/image"
    json_dir = "/home/ytusdc/Data/sdc/煤流检测/json"
    beginCheck(img_dir, json_dir, yaml_file)




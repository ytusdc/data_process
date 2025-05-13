import json
import cv2
from tqdm import tqdm
import os
from utils.yamloperate import get_id_cls_dict, write_yaml
import shutil
import numpy as np


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

def convert2yolo_txt(txt_path, height, width, labels_ls, points_ls, class_id_dict):

    with open(txt_path, "w") as f_w:
        for label, points in zip(labels_ls, points_ls):
            # 矩形转换成四边形
            if label == "qiegetou" and len(points) == 2:
                [x1, y1], [x2, y2] = points
                points = [[x1, y1], [x2, y1], [x2, y2], [x1, y2]]
            elif len(points) < 3:
                print(f"Error: must be at least 3 pairs: {txt_path} points lens= {len(points)}")
                # pass
            if label not in class_id_dict.keys():
                print(f"Error: unsupported label: {txt_path}: {label}")

            points_np = np.array(points, dtype=np.float64).reshape(-1, 2)
            # np_w = points_np[:, 0] < width
            # np_h = points_np[:, 1] < height
            # tmp_1 = np.where(np_w == False)[0]
            # tmp_2 = np.where(np_h == False)[0]
            # 保证标注点不超出边框
            clip_w = np.clip(points_np[:, 0], 0, width)
            clip_h = np.clip(points_np[:, 1], 0, height)
            point_clip = np.stack((clip_w, clip_h), axis=1)

            seg_ls = (point_clip / np.array([width, height])).reshape(-1).tolist()
            seg_ls = [class_id_dict[label]] + seg_ls
            line_tuple = (*seg_ls,)
            # 在保证六位有效数字的前提下，使用小数方式，否则使用科学计数法, 只适用于yolo，因为转换后都是小于1的数字
            f_w.write(("%g " * len(line_tuple)).rstrip() % line_tuple + "\n")

            # 因为使用round，会四舍五入 可能会出现还原超出边界问题
            # string_result = ""
            # for pt in points:
            #     string_result = string_result + " " + str(round(pt[0] / width, 6)) + " " + str(round(pt[1] / height, 6))
            # string_result = str(class_id_dict[label]) + " " + string_result + "\r"
            # f_w.write(string_result)

def getClassIndex(json_files, save_dir, yaml_file=None):
    if yaml_file is not None:
        id_cls_dict = get_id_cls_dict(yaml_file)
    else:
        category_set = set()
        # 先解析所有xml文件获取所有类别信息 category_set
        for json_file in tqdm(json_files):
            _, _, label_ls, _ = parse_json(json_file)
            category_set = category_set | set(label_ls)
        id_cls_dict = dict((k, v) for k, v in enumerate(sorted(category_set)))
        save_yaml_file = os.path.join(save_dir, "classes.yaml")
        write_yaml(save_yaml_file, id_cls_dict)
    class_indices_dict = dict((v, k) for k, v in id_cls_dict.items())
    return class_indices_dict
def begin_convert(ori_dir, save_dir, yaml_file=None):

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    json_files = [os.path.join(ori_dir, i) for i in os.listdir(ori_dir) if os.path.splitext(i)[-1] == '.json']
    class_indices = getClassIndex(json_files, save_dir, yaml_file)

    for json_path in tqdm(json_files):
        # print(json_path)
        height, width, label_ls, points_ls = parse_json(json_path)
        name = os.path.basename(json_path).split('.')[0]
        txt_path = os.path.join(save_dir, name + ".txt")
        convert2yolo_txt(txt_path, height, width, label_ls, points_ls, class_indices)

if __name__ == '__main__':

    ori_label_dir = "/home/ytusdc/Data_ori/caimeimian_images/json"
    # ori_label_dir = "/home/ytusdc/Data/ddd"
    save_dir = "/home/ytusdc/Data_ori/caimeimian_images/yolo"
    yam_file = "/home/ytusdc/Data/Data_caimeimian/caimeimian.yaml"
    begin_convert(ori_label_dir, save_dir, yam_file)

    pass
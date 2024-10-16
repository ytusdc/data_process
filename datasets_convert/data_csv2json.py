#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-08-21 10:07
Author  : sdc
"""
import json
import os
from pathlib import Path
from tqdm import tqdm

'''
json_data = {
    "filename": "",
    "width": 0,
    "height": 0,
    "object": [{}，{}，],
    "segment": [],
}
object 中是字典组成的列表
object_child = {
    "category": "",
    "bbox": [],  #矩形框 [xmin, ymin, xmax, ymax]
    "polygon": [[x1,y1], [x2,y2],[x3,y3]]  # 多边形
}
'''

def save_json(data_dict, save_path):
    with open(save_path, 'w') as f_r:
        json.dump(data_dict, f_r, indent=4, sort_keys=False)


def csv2json(csv_file, save_dir):

    with open(csv_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    lines_data = lines[1:]
    filename_set = set()
    for line in lines_data:
        row = line.strip().split(',')
        filename = row[0]
        filename_set.add(filename)

    for filename_id in tqdm(filename_set):
        data_dict = {
            "filename": "",
            "width": 0,
            "height": 0,
            "object": [],
            # "segment": [],
        }
        for line in lines_data:
            # 处理每一行数据
            row = line.strip().split(',')
            filename = row[0]

            if filename == filename_id:
                width = int(row[1])
                height = int(row[2])
                cls = row[3]
                xmin = float(row[4])
                ymin = float(row[5])
                xmax = float(row[6])
                ymax = float(row[7])
                box = [xmin, ymin, xmax, ymax]
                object_dict = {
                    "name": cls,
                    "bbox": box,
                }

                if filename in data_dict.keys():
                    data_dict["object"].append(object_dict)
                else:
                    data_dict["filename"] = filename
                    data_dict["width"] = width
                    data_dict["height"] = height
                    data_dict["object"].append(object_dict)

                name = Path(filename).stem
                save_file_path = os.path.join(save_dir, name + ".json")
                save_json(data_dict, save_file_path)



if __name__ == '__main__':

    file_path = "/home/ytusdc/Downloads/fire/Fire-and-smoke-in-open-area/json/val_annotations.csv"
    save = "/home/ytusdc/Downloads/fire/Fire-and-smoke-in-open-area/json/val"

    csv2json(file_path, save)


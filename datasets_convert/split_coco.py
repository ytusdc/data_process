#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-08-16 13:44
Author  : sdc
"""

import json
import os

def split_coco_json(input_file, output_dir):
    # 加载原始的COCO JSON文件
    with open(input_file, 'r') as f:
        coco_data = json.load(f)

    # 创建输出目录如果不存在的话
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 遍历所有的图片
    for img in coco_data['images']:
        image_id = img['id']
        annotations = [ann for ann in coco_data['annotations'] if ann['image_id'] == image_id]

        # 构建新的JSON结构
        output_data = {
            "info": coco_data['info'],
            "licenses": coco_data['licenses'],
            "images": [img],
            "annotations": annotations,
            "categories": coco_data['categories']
        }

        # 保存为新的JSON文件
        output_filename = f"{image_id}.json"
        output_path = os.path.join(output_dir, output_filename)
        with open(output_path, 'w') as out_f:
            json.dump(output_data, out_f, indent=4)

'''
coco数据拆分成单个文件
'''
if __name__ == "__main__":
    input_file = 'path/to/original/coco.json'  # 原始的COCO JSON文件路径
    output_dir = 'path/to/output/directory'    # 输出文件夹路径
    split_coco_json(input_file, output_dir)
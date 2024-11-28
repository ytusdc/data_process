import sys
sys.path.append("..")

import argparse
import json
import os
import sys
import shutil
from datetime import datetime
from utils import *
from datetime import datetime
import cv2
from pathlib import Path

coco = dict()
coco['images'] = []
coco['type'] = 'instances'
coco['annotations'] = []
coco['categories'] = []

image_set = set()

image_id = 000000
annotation_id = 0


def addCatItem(category_dict):
    for k, v in category_dict.items():
        category_item = dict()
        category_item['supercategory'] = 'none'
        category_item['id'] = int(k)
        category_item['name'] = v
        coco['categories'].append(category_item)

def addImgItem(file_name, size):
    global image_id
    image_id += 1
    image_item = dict()
    image_item['id'] = image_id
    image_item['file_name'] = file_name
    image_item['width'] = size[1]
    image_item['height'] = size[0]
    image_item['license'] = None
    image_item['flickr_url'] = None
    image_item['coco_url'] = None
    image_item['date_captured'] = str(datetime.today())
    coco['images'].append(image_item)
    image_set.add(file_name)
    return image_id


def addAnnoItem(object_name, image_id, category_id, bbox):
    global annotation_id
    annotation_item = dict()

    # yolo 检测数据集没有分割信息
    annotation_item['segmentation'] = []
    # seg = []
    # # bbox[] is x,y,w,h
    # # left_top
    # seg.append(bbox[0])
    # seg.append(bbox[1])
    # # left_bottom
    # seg.append(bbox[0])
    # seg.append(bbox[1] + bbox[3])
    # # right_bottom
    # seg.append(bbox[0] + bbox[2])
    # seg.append(bbox[1] + bbox[3])
    # # right_top
    # seg.append(bbox[0] + bbox[2])
    # seg.append(bbox[1])
    # annotation_item['segmentation'].append(seg)

    annotation_item['area'] = bbox[2] * bbox[3]
    annotation_item['iscrowd'] = 0
    annotation_item['ignore'] = 0
    annotation_item['image_id'] = image_id
    annotation_item['bbox'] = bbox
    annotation_item['category_id'] = category_id
    annotation_id += 1
    annotation_item['id'] = annotation_id
    coco['annotations'].append(annotation_item)

def convert2Coco(image_dir, yolo_path, yaml_file, save_path=None):
    assert os.path.exists(image_dir), "ERROR {} dose not exists".format(image_dir)
    assert os.path.exists(yolo_path), "ERROR {} dose not exists".format(yolo_path)

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    id_class_dict = utils_xml_opt.get_id_class_dict(yaml_file=yaml_file)
    addCatItem(id_class_dict)

    img_id_path_dict = common_fun.get_id_path_dict(image_dir)
    label_id_path_dict = common_fun.get_id_path_dict(yolo_path, suffix=".txt")

    img_id_set = set(img_id_path_dict.keys())

    for label_id, label_path in label_id_path_dict.items():
        if label_id not in img_id_set:
            print(f"error: 标签文件找不到对应图片文件, id: {label_id}")
            continue
        img_path = img_id_path_dict[label_id]
        img = cv2.imread(img_path)
        shape = img.shape  # (h, w, c)
        size = (shape[1], shape[0])
        filename = Path(img_path).name
        current_image_id = addImgItem(filename, shape)
        # 读取yolo标签文件
        with open(label_path, 'r') as f_r:
            for line in f_r.readlines():
                line = line.strip().split()
                category = int(line[0])
                category_name = id_class_dict[category]
                bbox = utils_yolo_opt.xywhn2xywh((line[1], line[2], line[3], line[4]), size)
                addAnnoItem(category_name, current_image_id, category, bbox)
    timestamp = datetime.now().timestamp()
    # 将时间戳转换为日期时间对象
    formatted_string = datetime.fromtimestamp(timestamp).strftime('%Y%m%d_%H%M%S')

    json_path = os.path.join(save_path, formatted_string + ".json")
    json.dump(coco, open(json_path, 'w'))
    print("class nums:{}".format(len(coco['categories'])))
    print("image nums:{}".format(len(coco['images'])))
    print("bbox nums:{}".format(len(coco['annotations'])))
    print(f"转换后json文件: {json_path}")



if __name__ == '__main__':
    """
    脚本说明：
        本脚本用于将yolo格式的标注文件.txt转换为coco格式的标注文件.json
    参数说明：
        image_path: 图片路径
        anno_path: image_path 对应的标注文件txt存储路径（yolo格式）
        save_path: json文件输出的文件夹
        json_name: json文件名字
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--image-dir', type=str, default='./data/images')
    parser.add_argument('-y', '--yolo-dir', type=str, default='./data/labels/yolo', help='yolo 标签路径')
    parser.add_argument('-f', '--yaml-file', type=str, default=None, help='yaml file 文件路径')
    parser.add_argument('-s', '--save-path', type=str, default='./data/convert/coco', help='json save path')

    opt = parser.parse_args()
    input_args = sys.argv[1:]  # 第一个参数是脚本名本身
    if len(input_args) > 0:
        if opt.image_dir is None or opt.yolo_dir is None or opt.yaml_file:
            print("图片文件路径，yolo 文件路径和yaml file 文件不能为空, 退出脚本！")
            sys.exit(-1)
        image_dir = opt.image_dir
        yolo_dir = opt.yolo_dir
        yaml_file = opt.yaml_file
        save_path = opt.save_path
    else:
        image_dir = './data/images'
        yolo_dir = './data/labels/yolo'
        yaml_file = ''
        save_path = 'result/convert/coco'

    convert2Coco(image_dir, yolo_dir, yaml_file, save_path)

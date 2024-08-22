import os
import json
import argparse
import sys
import shutil
from tqdm import tqdm
from pathlib import Path

from utils.yamloperate import read_yaml, write_yaml, get_id_cls_dict

def xyxy2xywhn(bbox, size):
    bbox = list(map(float, bbox))
    size = list(map(float, size))
    xc = (bbox[0] + (bbox[2] - bbox[0]) / 2.) / size[0]
    yc = (bbox[1] + (bbox[3] - bbox[1]) / 2.) / size[1]
    wn = (bbox[2] - bbox[0]) / size[0]
    hn = (bbox[3] - bbox[1]) / size[1]
    return (xc, yc, wn, hn)

def parser_info(info: dict, class_indices=None):
    filename = info['filename']

    objects = []
    width = int(info['width'])
    height = int(info['height'])

    if 'object' not in info.keys():
        print(filename)
        return filename, []

    for obj in info['object']:
        obj_name = obj['name']
        xmin = float(obj['bbox'][0])
        ymin = float(obj['bbox'][1])
        xmax = float(obj['bbox'][2])
        ymax = float(obj['bbox'][3])
        bbox = xyxy2xywhn((xmin, ymin, xmax, ymax), (width, height))
        if class_indices is not None:
            obj_category = class_indices[obj_name]
            object = [obj_category, bbox]
            objects.append(object)
    # print(filename)
    return filename, objects

def parse_obj_name(info: dict):
    names_set = set()
    filename = info['filename']
    if 'object' not in info.keys():
        print(f"{filename}, have not object")
        return None
    for obj in info['object']:
        obj_name = obj['name']
        names_set.add(obj_name)
    return names_set
def getClassIndex(json_files, save_dir, yaml_file=None):

    if yaml_file is not None:
        id_cls_dict = get_id_cls_dict(yaml_file)
    else:
        category_set = set()
        # 先解析所有xml文件获取所有类别信息 category_set
        for json_file in json_files:
            with open(json_file, 'r') as f_r:
                json_dict = json.load(f_r)
            # category_set.union(parse_obj_name(json_dict))
            category_set = category_set | parse_obj_name(json_dict)
        id_cls_dict = dict((k, v) for k, v in enumerate(sorted(category_set)))
        save_yaml_file = os.path.join(save_dir, "classes.yaml")
        write_yaml(save_yaml_file, id_cls_dict)

    class_indices_dict = dict((v, k) for k, v in id_cls_dict.items())
    return class_indices_dict

def parseJsonFiles(json_dir, save_dir, yaml_file=None):
    assert os.path.exists(json_dir), "ERROR {} does not exists".format(json_dir)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    else:
        # shutil.rmtree(save_dir)
        pass

    json_files = [os.path.join(json_dir, i) for i in os.listdir(json_dir) if os.path.splitext(i)[-1] == '.json']
    class_indices = getClassIndex(json_files, save_dir, yaml_file)
    json_files = tqdm(json_files)
    for json_file in json_files:
        with open(json_file, 'r') as f_r:
            json_dict = json.load(f_r)

        filename, objects = parser_info(json_dict, class_indices=class_indices)
        # name =
        txt_file = os.path.join(save_dir, Path(filename).stem + ".txt")
        if len(objects) != 0:
            with open(txt_file, 'w') as f:
                for obj in objects:
                    f.write(
                        "{} {:.5f} {:.5f} {:.5f} {:.5f}\n".format(obj[0], obj[1][0], obj[1][1], obj[1][2], obj[1][3]))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--json-dir', type=str, default='./data/labels/voc')
    parser.add_argument('--save-dir', type=str, default='./data/convert/yolo')
    parser.add_argument('--yaml-file', type=str, default="./yaml/yolo_sample.yaml")
    opt = parser.parse_args()
    if len(sys.argv) > 1:
        print(opt)
        parseJsonFiles(**vars(opt))
    else:
        # voc_xml_dir = './data/labels/voc'
        # save_dir = './data/convert/yolo'
        # yaml_file = "./yaml/yolo_sample.yaml"
        yaml_file = None
        json_dir = '/home/ytusdc/Downloads/fire/Fire-and-smoke-in-open-area/json/val'
        save_dir = '/home/ytusdc/Downloads/fire/Fire-and-smoke-in-open-area/labels/val'
        yaml_file = "/home/ytusdc/Downloads/fire/Fire-and-smoke-in-open-area/json/classes.yaml"

        parseJsonFiles(json_dir, save_dir, yaml_file)



import os
import json
import argparse
import sys
import shutil
from lxml import etree
from tqdm import tqdm

from utils.yamloperate import read_yaml, write_yaml, get_id_cls_dict

category_set = set()
image_set = set()
bbox_nums = 0

def parse_xml_to_dict(xml):
    """
    将xml文件解析成字典形式，参考tensorflow的recursive_parse_xml_to_dict
    Args:
        xml: xml tree obtained by parsing XML file contents using lxml.etree

    Returns:
        Python dictionary holding XML contents.
    """
    if len(xml) == 0:  # 遍历到底层，直接返回tag对应的信息
        return {xml.tag: xml.text}

    result = {}
    for child in xml:
        child_result = parse_xml_to_dict(child)  # 递归遍历标签信息
        if child.tag != 'object':
            result[child.tag] = child_result[child.tag]
        else:
            if child.tag not in result:  # 因为object可能有多个，所以需要放入列表里
                result[child.tag] = []
            result[child.tag].append(child_result[child.tag])
    return {xml.tag: result}

def xyxy2xywhn(bbox, size):
    bbox = list(map(float, bbox))
    size = list(map(float, size))
    xc = (bbox[0] + (bbox[2] - bbox[0]) / 2.) / size[0]
    yc = (bbox[1] + (bbox[3] - bbox[1]) / 2.) / size[1]
    wn = (bbox[2] - bbox[0]) / size[0]
    hn = (bbox[3] - bbox[1]) / size[1]
    return (xc, yc, wn, hn)

def parser_info(info: dict, only_cat=True, class_indices=None):
    filename = info['annotation']['filename']
    image_set.add(filename)
    objects = []
    width = int(info['annotation']['size']['width'])
    height = int(info['annotation']['size']['height'])
    for obj in info['annotation']['object']:
        obj_name = obj['name']
        category_set.add(obj_name)
        if only_cat:
            continue
        xmin = int(obj['bndbox']['xmin'])
        ymin = int(obj['bndbox']['ymin'])
        xmax = int(obj['bndbox']['xmax'])
        ymax = int(obj['bndbox']['ymax'])
        bbox = xyxy2xywhn((xmin, ymin, xmax, ymax), (width, height))
        if class_indices is not None:
            obj_category = class_indices[obj_name]
            object = [obj_category, bbox]
            objects.append(object)

    return filename, objects

def getClassIndex(xml_files, yaml_file=None):

    if yaml_file is not None:
        id_cls_dict = get_id_cls_dict(yaml_file)
    else:
        # 先解析所有xml文件获取所有类别信息 category_set
        for xml_file in xml_files:
            with open(xml_file) as fid:
                xml_str = fid.read()
            xml = etree.fromstring(xml_str)
            info_dict = parse_xml_to_dict(xml)
            parser_info(info_dict, only_cat=True)

        id_cls_dict = dict((k, v) for k, v in enumerate(sorted(category_set)))
        # yaml_dict["names"] = id_cls_dict
        save_yaml_file = os.path.join(save_dir, "classes.yaml")
        write_yaml(save_yaml_file, id_cls_dict)

    class_indices_dict = dict((v, k) for k, v in id_cls_dict.items())
    return class_indices_dict

def parseXmlFilse(voc_dir, save_dir, yaml_file=None):
    assert os.path.exists(voc_dir), "ERROR {} does not exists".format(voc_dir)
    if os.path.exists(save_dir):
        shutil.rmtree(save_dir)
    os.makedirs(save_dir)

    xml_files = [os.path.join(voc_dir, i) for i in os.listdir(voc_dir) if os.path.splitext(i)[-1] == '.xml']
    class_indices = getClassIndex(xml_files, yaml_file)

    xml_files = tqdm(xml_files)
    for xml_file in xml_files:
        with open(xml_file) as fid:
            xml_str = fid.read()
        xml = etree.fromstring(xml_str)
        info_dict = parse_xml_to_dict(xml)
        filename, objects = parser_info(info_dict, only_cat=False, class_indices=class_indices)
        if len(objects) != 0:
            global bbox_nums
            bbox_nums += len(objects)
            with open(save_dir + "/" + filename.split(".")[0] + ".txt", 'w') as f:
                for obj in objects:
                    f.write(
                        "{} {:.5f} {:.5f} {:.5f} {:.5f}\n".format(obj[0], obj[1][0], obj[1][1], obj[1][2], obj[1][3]))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--voc-dir', type=str, default='./data/labels/voc')
    parser.add_argument('--save-dir', type=str, default='./data/convert/yolo')
    parser.add_argument('--yaml-file', type=str, default="./yaml/yolo_sample.yaml")
    opt = parser.parse_args()
    if len(sys.argv) > 1:
        print(opt)
        parseXmlFilse(**vars(opt))
        print("image nums: {}".format(len(image_set)))
        print("category nums: {}".format(len(category_set)))
        print("bbox nums: {}".format(bbox_nums))
    else:
        voc_dir = './data/labels/voc'
        save_dir = './data/convert/yolo'
        yaml_file = "./yaml/yolo_sample.yaml"

        # parseXmlFilse(voc_dir, save_dir, yaml_file)
        parseXmlFilse(voc_dir, save_dir)
        print("image nums: {}".format(len(image_set)))
        print("category nums: {}".format(len(category_set)))
        print("bbox nums: {}".format(bbox_nums))

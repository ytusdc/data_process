import xml.etree.ElementTree as ET
from lxml import etree
import yaml
import os
import shutil

'''
修改特定元素值, 保存并且覆盖原文件
使用前最好有备份
xml_file: xml 文件
element: 需要改变的标签
elem_value: 修改后的标签内容
'''

def modify_elem(xml_file, element, elem_value):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    # nodes = root.findall('.//filename')
    nodes = root.findall(element)
    for node in nodes:
        node.text = elem_value

    tree.write(xml_file, encoding='utf-8')


'''
从 yaml 文件中读取数据 
'''
def get_cls_names_set(file_path):
    def read_yaml(file_path):
        with open(file_path, 'r') as file:
            data = yaml.safe_load(file)
        return data

    yaml_dict = read_yaml(file_path)
    return set(yaml_dict["names"].values())


def mkdirs(full_path_dir):
    if not os.path.exists(full_path_dir):
        os.makedirs(full_path_dir)
def move_file(source_path, destination_path):
    shutil.move(source_path, destination_path)

def move_files(img_file, xml_file, move_dir_path):
    mkdirs(move_dir_path)
    move_file(img_file, move_dir_path)
    move_file(xml_file, move_dir_path)





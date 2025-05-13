import os
import json
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw
from lxml import etree, objectify
import numpy as np
from tqdm import tqdm
from utils import common
from pathlib import Path

def find_axis_aligned_bounding_box(points):
    """
    找到给四个定点集的平行于坐标轴的最小外接矩形。
    :param points: 四边形的顶点坐标列表，格式为 [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    :return: 最小外接矩形的四个顶点坐标
    """
    # 将点集转换为 NumPy 数组
    points = np.array(points, dtype=np.float32)
    # print(points)

    # 计算边界
    min_x = np.min(points[:, 0])
    max_x = np.max(points[:, 0])
    min_y = np.min(points[:, 1])
    max_y = np.max(points[:, 1])

    # 生成矩形的四个顶点
    bounding_box = [
        [min_x, min_y],  # 左下角
        [max_x, min_y],  # 右下角
        [max_x, max_y],  # 右上角
        [min_x, max_y]  # 左上角
    ]

    # return np.array(bounding_box, dtype=np.int32)
    return  [min_x, min_y], [max_x, max_y]

def save_info_dict_to_xml(info_dict, img_name, save_path):
    """
    保存字典信息到xml
    Args:
        info_dict:
        save_path:
    Returns:
    """

    objs = info_dict['shapes']
    h, w = info_dict['imageHeight'], info_dict['imageWidth']

    E = objectify.ElementMaker(annotate=False)
    anno_tree = E.annotation(
        E.folder("voc 2012"),
        E.filename(img_name),
        E.source(
            E.database("The VOC Database"),
            E.annotation("PASCAL VOC"),
            E.image("flickr")
        ),
        E.size(
            E.width(w),
            E.height(h),
            E.depth("3")
        ),
        E.segmented(0)

    )
    for obj in objs:
        points_ls = obj["points"]
        if len(points_ls) != 4:
            continue

        left_top_point, right_bottom_point = find_axis_aligned_bounding_box(points_ls)

        name_cls = obj["label"]
        if name_cls == "coalwall":
            # print(name_cls)
            continue

        E2 = objectify.ElementMaker(annotate=False)
        sub_anno_tree = E2.object(
            E.name(name_cls),
            E.pose('Unspecified'),
            E.truncated(0),
            E.difficult(0),
            E.occluded(0),
            E.bndbox(
                E.xmin(int(left_top_point[0])),
                E.ymin(int(left_top_point[1])),
                E.xmax(int(right_bottom_point[0])),
                E.ymax(int(right_bottom_point[1]))
            )
        )
        anno_tree.append(sub_anno_tree)
    etree.ElementTree(anno_tree).write(save_path, pretty_print=True)


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


# 示例用法
if __name__ == "__main__":

    # 转换并保存
    # create_voc_annotation(json_data, output_dir)
    image_dir = "/home/ytusdc/Data_ori/caimeimian_images/image"
    json_dir = "/home/ytusdc/Data_ori/caimeimian_images/json"
    save_dir = "/home/ytusdc/Data_ori/caimeimian_images/out"

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    json_files = [os.path.join(json_dir, i) for i in os.listdir(json_dir) if os.path.splitext(i)[-1] == '.json']
    json_files = [os.path.join(json_dir, i) for i in os.listdir(json_dir) if os.path.splitext(i)[-1] in ['.jpg', 'png']]

    id_image_files = common.get_id_path_dict(image_dir, ['.png', '.jpg'])
    id_json_files = common.get_id_path_dict(json_dir,['.json'])

    common_id_set =  set(id_image_files.keys()) & set(id_json_files.keys())


    for common_id in tqdm(common_id_set):
        img_name = Path(id_image_files[common_id]).name
        json_name = Path(id_json_files[common_id]).name
        json_path = id_json_files[common_id]

        name = os.path.basename(json_path).split('.')[0]
        save_xml_file = os.path.join(save_dir, name + ".xml")
        # print(json_path)
        with open(json_path, "r") as file_r:
            json_dict = json.load(file_r)

        save_info_dict_to_xml(json_dict, img_name, save_xml_file)

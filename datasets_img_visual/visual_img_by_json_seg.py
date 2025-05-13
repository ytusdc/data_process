import os
import cv2
import numpy as np
import json
from matplotlib import pyplot as plt
from tqdm import tqdm
from pathlib import Path
from utils import common_fun
from utils.yamloperate import get_id_cls_dict
from utils.colortable import get_color_rgb, get_color_bgr

'''
# 加载JSON数据, 示例
json_data = {
    "shapes": [
        {
            "label": "3",
            "points": [
                [34, 348],
                [118, 331],
                [158, 292],
                [317, 284],
                [340, 241],
            ],
            "shape_type": "polygon",
            "mask": 0
        }
    ],
    "imagePath": "Snipaste_2025-02-18_11-04-02.png",
    "imageHeight": 922,
    "imageWidth": 1790
}
'''

global_cls_id_dict = None

'''
在原有图中叠加分割区域
'''
def draw_seg_mask(json_file, img_file):
    if global_cls_id_dict is None:
        raise FileNotFoundError(f"进行掩码叠加时，yaml 文件不能为空，否则图片掩码颜色一致不方便区分")
    # 加载图像
    image = cv2.imread(img_file)
    if image is None:
        raise FileNotFoundError(f"Image not found: {img_file}")

    with open(json_file, "r") as f:
        json_data = json.load(f)
    img_h = json_data["imageHeight"]
    img_w = json_data["imageWidth"]
    # 创建原图大小掩码
    mask = np.zeros((img_h, img_w, 3), dtype=np.uint8)      # 三通道有颜色的值的 mask
    mask_binary = np.zeros((img_h, img_w), dtype=np.uint8)  # 单通道二值 mask
    # 遍历每个标注形状
    for shape in json_data["shapes"]:
        label = shape["label"]
        points = np.array(shape["points"], dtype=np.int32).reshape((-1, 1, 2))
        # 根据标签选择颜色
        color = get_color_bgr(global_cls_id_dict[label])  # 根据标签选择颜色
        # 绘制并用颜色填充多边形
        cv2.fillPoly(mask, [points], color)
        # cv2.fillPoly(mask_binary, [points], 255)
        # 绘制填充区域边界框（可选）
        # cv2.polylines(mask, [points], isClosed=True, color=(0, 255, 0), thickness=2)

    # 将掩码叠加到图像上
    alpha = 0.3
    result = cv2.addWeighted(mask, alpha, image, 1 - alpha, 0)
    return result

'''
在原有图中绘制分割多边形
'''
def draw_seg_line(json_file, img_file):
    line_color_default = (0, 0, 255)
    with open(json_file, "r") as f:
        json_data = json.load(f)
    # 加载图像
    image = cv2.imread(img_file)
    if image is None:
        raise FileNotFoundError(f"Image not found: {img_file}")
    # 遍历每个标注形状
    for shape in json_data["shapes"]:
        label = shape["label"]
        points = np.array(shape["points"], dtype=np.int32).reshape((-1, 1, 2))

        # 根据标签id(0, 1, 2)选择颜色
        if global_cls_id_dict is None:
            color = line_color_default
        else:
            color = get_color_bgr(global_cls_id_dict[label])
        # 绘制边界框
        cv2.polylines(image, [points], isClosed=True, color=color, thickness=2)
    return image

def draw_image(imgs_dir, annos_dir, imgs_save_dir, yaml_file=None, img_type=['.jpg', '.png', '.jpeg']):
    """
    Args:
        imgs_dir:    图片文件数据
        annos_dir:   标签文件数据
        imgs_save_dir:  可视化后文件保存位置
        yaml_file:   id:name 标签对应文件，有id号才能根据id绘制颜色，否则都绘制同一种颜色
        img_type: 过滤的图片文件类型， 默认['.jpg', '.png', '.jpeg']
    Returns:
    """
    assert os.path.exists(imgs_dir), "image path:{} dose not exists".format(image_path)
    assert os.path.exists(annos_dir), "annotation path:{} does not exists".format(annos_dir)
    if not os.path.exists(imgs_save_dir):
        os.makedirs(imgs_save_dir)
    anno_file_list = [os.path.join(annos_dir, file) for file in os.listdir(annos_dir) if file.endswith(".json")]
    # img_file_list =

    img_id_path_dict = common_fun.get_id_path_dict(imgs_dir, img_type)
    label_id_path_dict = common_fun.get_id_path_dict(annos_dir, ".json")
    common_id_set = set(img_id_path_dict.keys()) & set(label_id_path_dict.keys())

    if yaml_file is not None:
        id_cls_dict = get_id_cls_dict(yaml_file)
        global global_cls_id_dict
        global_cls_id_dict = dict((v, k) for k, v in id_cls_dict.items())

    for common_id in tqdm(sorted(common_id_set)):
        img_file = img_id_path_dict[common_id]
        json_file = label_id_path_dict[common_id]
        img_result = draw_seg_mask(json_file, img_file)
        save_img_file = Path(imgs_save_dir, Path(img_file).name)
        cv2.imwrite(str(save_img_file), img_result)

        # cv2.namedWindow("show", cv2.WINDOW_NORMAL)
        # # cv2.resizeWindow("show", 800, 600)
        # cv2.imshow("show", mask)
        # # 调整窗口大小（可选）
        # cv2.waitKey(0)

if __name__ == '__main__':
    image_path = os.path.join("/home/ytusdc/Pictures/meimian", "Snipaste_2025-02-18_11-04-02.png")
    json_file = "/home/ytusdc/Pictures/meimian/Snipaste_2025-02-18_11-04-02.json"

    images_dir = "/home/ytusdc/Pictures/test_meimian"
    annos_dir = "/home/ytusdc/Pictures/test_meimian"
    yaml_file = "/home/ytusdc/Data/Data_caimeimian/caimeimian.yaml"
    imgs_save_dir = "/home/ytusdc/Pictures/test_meimian_visual"
    # yaml_file = None

    # images_dir = "/home/ytusdc/Data/Data_caimeimian/img_ori"
    # annos_dir = "/home/ytusdc/Data/Data_caimeimian/json"
    # yaml_file = "/home/ytusdc/Data/Data_caimeimian/caimeimian.yaml"
    # imgs_save_dir = "/home/ytusdc/Data/Data_caimeimian/result_img"

    draw_image(images_dir, annos_dir, imgs_save_dir, yaml_file =yaml_file )

    # draw_seg_mask(json_file)
    pass
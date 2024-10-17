import os
import cv2
import matplotlib.pyplot as plt
from tqdm import tqdm
from collections import defaultdict
import argparse
import sys
import datetime
from utils.colortable import get_color_rgb, get_color_bgr
import json

category_id_dict = dict()
global_category_id = -1

"""
imgs_dir: 原始图片所在路径
annos_dir： 标签文件所在路径
imgs_save_dir： 绘制 bbox后的img存储位置
bgr： 颜色值格式为bgr，使用opencv绘图颜色值是bgr， 如果是rgb格式颜色值需要做相应转换
"""
def draw_box(json_file_path, image_dir, save_dir, bgr=True):
    with open(json_file_path) as f_r:
        json_dict = json.load(f_r)
    filename = json_dict["filename"]
    file_path = os.path.join(image_dir, filename)
    if not os.path.exists(file_path):
        print(f"have not find imgfile: {file_path}")
        return
    img = cv2.imread(file_path)
    if img is None:
        print(f"cv2 read img error: {file_path}")
        return

    if 'object' in json_dict.keys():
        objects = json_dict['object']
    else:
        print(f"{json_file_path} have not object")
        return

    for object in objects:
        category_name = object['name']
        if category_name not in category_id_dict:
            category_id = addCatItem(category_name)
        else:
            category_id = category_id_dict[category_name]

        xmin = int(float(object['bbox'][0]))
        ymin = int(float(object['bbox'][1]))
        xmax = int(float(object['bbox'][2]))
        ymax = int(float(object['bbox'][3]))

        if bgr:
            color = get_color_bgr(category_id)
        else:
            color = get_color_rgb(category_id)
        cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, thickness=2)
        cv2.putText(img, category_name, (xmin, ymin), cv2.FONT_HERSHEY_SIMPLEX, 2, color, thickness=2)
        cv2.imwrite(os.path.join(save_dir, filename), img)

def addCatItem(name):
    global global_category_id
    category_item_id += 1
    category_id_dict[name] = category_item_id
    return category_item_id


"""
imgs_dir: 原始图片所在路径
annos_dir： 标签文件所在路径
imgs_save_dir： 绘制 bbox后的img存储位置
"""
def draw_image(imgs_dir, annos_dir, imgs_save_dir):
    assert os.path.exists(imgs_dir), "image path:{} dose not exists".format(image_path)
    assert os.path.exists(annos_dir), "annotation path:{} does not exists".format(anno_path)
    if not os.path.exists(imgs_save_dir):
        os.makedirs(imgs_save_dir)
    anno_file_list = [os.path.join(annos_dir, file) for file in os.listdir(anno_path) if file.endswith(".json")]

    for json_file in tqdm(anno_file_list):
        draw_box(json_file, imgs_dir, imgs_save_dir)
        # show:
        #     cv2.imshow(filename, img)
        #     cv2.waitKey()
        #     cv2.destroyAllWindows()

if __name__ == '__main__':
    """
    脚本说明：
        该脚本用于 json 标注格式（.json）的标注框可视化
    参数明说：
        imgs-dir:图片数据路径
        anno-dir:json标注文件路径
        save-dir:绘制bbox后，图片存储路径
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', '--imgs-dir', type=str, default='./data/images', help='image path')
    parser.add_argument('-ap', '--anno-dir', type=str, default='./data/labels/voc', help='annotation path')
    parser.add_argument('-s', '--save-dir', default='./data/savefolder', help='image save path')
    opt = parser.parse_args()

    if len(sys.argv) > 1:
        print(opt)
        draw_image(opt.imgs_dir, opt.anno_dir, opt.save_dir)
        print("category nums: {}".format(len(category_id_dict)))
    else:
        image_path = '/home/ytusdc/Downloads/fire/Fire-and-smoke-in-open-area/images/train'
        anno_path = '/home/ytusdc/Downloads/fire/Fire-and-smoke-in-open-area/json/train'
        save_img_dir = '/home/ytusdc/Downloads/fire/Fire-and-smoke-in-open-area/visual'
        draw_image(image_path, anno_path, save_img_dir)
        print("category nums: {}".format(len(category_id_dict)))


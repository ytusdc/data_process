import argparse
import os
import sys
from collections import defaultdict

import cv2
import matplotlib

from pathlib import Path

from utils.colortable import get_color_rgb

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from tqdm import tqdm
import datetime

from utils.yamloperate import get_id_cls_dict
from utils.colortable import get_color_rgb, get_color_bgr

category_set = dict()

every_class_num = defaultdict(int)
category_item_id = -1

def xywhn2xyxy(box, size):
    box = list(map(float, box))
    size = list(map(float, size))
    xmin = (box[0] - box[2] / 2.) * size[0]
    ymin = (box[1] - box[3] / 2.) * size[1]
    xmax = (box[0] + box[2] / 2.) * size[0]
    ymax = (box[1] + box[3] / 2.) * size[1]
    return (xmin, ymin, xmax, ymax)


def addCatItem(name):
    global category_item_id
    category_item = dict()
    category_item_id += 1
    category_item['id'] = category_item_id
    category_item['name'] = name
    category_set[name] = category_item_id
    return category_item_id


def get_id_path_dict(data_dir, file_suffix=['.jpg', '.png', '.jpeg']):
    file_ls = []
    # 过滤掉 ‘.’开头的隐藏文件, 有的情况下会出现，大部分情况不会，以防万一
    filter_file_ls = os.listdir(data_dir)
    for i in range(len(filter_file_ls) - 1, -1, -1):  # for i in range(0, num_list.__len__())[::-1]
        if filter_file_ls[i].startswith('.'):
            filter_file_ls.pop(i)

    if file_suffix is None:
        file_ls = filter_file_ls
    # 根据文件后缀过滤
    elif isinstance(file_suffix, str):
        file_ls = list(filter(lambda x: x.endswith(file_suffix), filter_file_ls))
    elif isinstance(file_suffix, list):
        file_ls = [file_name for file_name in filter_file_ls
                  if os.path.splitext(file_name)[-1] in file_suffix]
        # for suffix in file_suffix:
        #     child_ls = list(filter(lambda x: x.endswith(suffix), os.listdir(data_dir)))
        #     file_ls.extend(child_ls)

    sorted_file_ls = sorted(file_ls)  # 排序，保证各平台顺序一致
    return sorted_file_ls


"""
imgs_dir: 原始图片所在路径
annos_dir： 标签文件所在路径
imgs_save_dir： 绘制 bbox后的img存储位置
yaml_file: yolo 标签对应类别的文件
bgr： 颜色值格式为bgr，使用opencv绘图颜色值是bgr， 如果是rgb格式颜色值需要做相应转换
"""
def draw_image(imgs_dir, annos_dir,  imgs_save_dir, yaml_file=None, bgr=True):
    assert os.path.exists(imgs_dir), "image path:{} dose not exists".format(imgs_dir)
    assert os.path.exists(annos_dir), "annotation path:{} does not exists".format(annos_dir)
    if not os.path.exists(imgs_save_dir):
        os.makedirs(imgs_save_dir)

    # anno_file_list = [os.path.join(annos_dir, file) for file in os.listdir(annos_dir) if file.endswith(".txt")]
    img_type = {'.jpg', '.png', '.jpeg'}
    img_id_dict = {Path(i).stem: os.path.join(imgs_dir, i) for i in os.listdir(imgs_dir) if os.path.splitext(i)[-1] in img_type}
    label_id_dict = {Path(i).stem: os.path.join(annos_dir, i) for i in os.listdir(annos_dir) if os.path.splitext(i)[-1]=='.txt'}


    if yaml_file is not None:
        category_id_dict = get_id_cls_dict(yaml_file)

    for id in tqdm(label_id_dict.keys()):
        label_file = label_id_dict[id]
        img_file = img_id_dict[id]

        filename = os.path.basename(img_file)

        # filename = img_file.split(os.sep)[-1].split('.')[0] + ".jpg"
        img = cv2.imread(img_file)
        if img is None:
            print(f"{img_file} read is None")
            return
        height, width, _ = img.shape

        objects = []
        with open(label_file, 'r') as fid:
            for line in fid.readlines():
                line = line.strip().split()
                if yaml_file is not None:
                    category_name = category_id_dict[int(line[0])]
                else:
                    category_name = str(line[0])
                bbox = xywhn2xyxy((line[1], line[2], line[3], line[4]), (width, height))
                obj = [category_name, bbox]
                objects.append(obj)

        for object in objects:
            category_name = object[0]
            every_class_num[category_name] += 1
            if category_name not in category_set:
                category_id = addCatItem(category_name)
            else:
                category_id = category_set[category_name]
            xmin = int(float(object[1][0]))
            ymin = int(float(object[1][1]))
            xmax = int(float(object[1][2]))
            ymax = int(float(object[1][3]))

            if bgr:
                color = get_color_bgr(category_id)
            else:
                color = get_color_rgb(category_id)

            cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, thickness=2)
            cv2.putText(img, category_name, (xmin - 10, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, thickness=2)
            cv2.imwrite(os.path.join(imgs_save_dir, filename), img)

    # 默认统计信息
    statistics_info()

"""
统计信息，并且绘制柱形图，然后输出结果
"""
def statistics_info():

    # 绘制每种类别个数柱状图
    plt.bar(range(len(every_class_num)), every_class_num.values(), align='center')
    # 将横坐标0,1,2,3,4替换为相应的类别名称
    plt.xticks(range(len(every_class_num)), every_class_num.keys(), rotation=90)
    # 在柱状图上添加数值标签
    for index, (cls, num) in enumerate(every_class_num.items()):
        plt.text(x=index, y=num, s=str(num), ha='center')
        # print(f"{cls}:{num}")

    # 设置x坐标
    plt.xlabel('image class')
    # 设置y坐标
    plt.ylabel('number of images')
    # 设置柱状图的标题
    plt.title('class distribution')
    # 保存柱状图
    now = datetime.datetime.now()
    time_str = now.strftime('%Y%m%d-%H%M%S')
    plt.savefig(f"class_distribution_{time_str}.png")
    # plt.show()


if __name__ == '__main__':
    """
    脚本说明：
        该脚本用于yolo标注格式（.txt）的标注框可视化
    参数明说：
        imgs-dir:图片数据路径
        anno-dir:xml标注文件路径
        save-dir:绘制bbox后，图片存储路径
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-ip', '--imgs-dir', type=str, default='./data/images', help='image path')
    parser.add_argument('-ap', '--anno-dir', type=str, default='./data/labels/voc', help='annotation path')
    parser.add_argument('-s', '--save-dir', default='./data/savefolder', help='image save path')
    parser.add_argument('-yaml', '--yaml-file', default='', help='yaml file path')
    opt = parser.parse_args()

    if len(sys.argv) > 1:
        print(opt)
        draw_image(opt.imgs_dir, opt.anno_dir, opt.yaml_file, opt.save_dir)
        print(every_class_num)
        print("category nums: {}".format(len(category_set)))
        print("bbox nums: {}".format(sum(every_class_num.values())))
    else:
        # image_path = './data/images'
        # anno_path = './data/convert/yolo'
        # save_img_dir = './data/save'
        # yaml_file = "./yaml/coco_hat.yaml"

        image_path = '/home/ytusdc/project-10-at-2024-09-29-15-10-594eb3fb/images'
        anno_path = '/home/ytusdc/project-10-at-2024-09-29-15-10-594eb3fb/labels'
        save_img_dir = '/home/ytusdc/project-10-at-2024-09-29-15-10-594eb3fb/visual'
        # yaml_file = "/home/ytusdc/Downloads/Smoking-and-Drinking-Dataset-for-YOLO/Dataset/data_2.yaml"

        draw_image(image_path, anno_path, save_img_dir)
        print(every_class_num)
        print("category nums: {}".format(len(category_set)))
        print("bbox nums: {}".format(sum(every_class_num.values())))

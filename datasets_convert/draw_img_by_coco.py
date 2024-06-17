import argparse
import os
import sys
from collections import defaultdict
from xml import etree
from pycocotools.coco import COCO

import cv2
import matplotlib
import datetime

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from tqdm import tqdm
from utils.colortable import get_color_rgb, get_color_bgr

category_set = dict()
image_set = set()
every_class_num = defaultdict(int)

category_item_id = -1


def addCatItem(name):
    global category_item_id
    category_item = dict()
    category_item_id += 1
    category_item['id'] = category_item_id
    category_item['name'] = name
    category_set[name] = category_item_id
    return category_item_id

# 将类别名字和id建立索引
def catid2name(coco):
    classes = dict()
    for cat in coco.dataset['categories']:
        classes[cat['id']] = cat['name']
    return classes


"""
imgs_dir: 原始图片所在路径
annos_dir： 标签文件所在路径
imgs_save_dir： 绘制 bbox后的img存储位置
bgr： 颜色值格式为bgr，使用opencv绘图颜色值是bgr， 如果是rgb格式颜色值需要做相应转换
"""
def draw_image(imgs_dir, annos_dir, imgs_save_dir, bgr=True):
    assert os.path.exists(imgs_dir), "image path:{} dose not exists".format(imgs_dir)
    assert os.path.exists(annos_dir), "annotation path:{} does not exists".format(annos_dir)
    if not annos_dir.endswith(".json"):
        raise RuntimeError("ERROR {} dose not a json file".format(annos_dir))

    if not os.path.exists(imgs_save_dir):
        os.makedirs(imgs_save_dir)

    coco = COCO(annos_dir)
    classes = catid2name(coco)
    imgIds = coco.getImgIds()
    classesIds = coco.getCatIds()
    for imgId in tqdm(imgIds):
        size = {}
        img = coco.loadImgs(imgId)[0]
        filename = img['file_name']
        image_set.add(filename)
        width = img['width']
        height = img['height']
        size['width'] = width
        size['height'] = height
        size['depth'] = 3
        annIds = coco.getAnnIds(imgIds=img['id'], iscrowd=None)
        anns = coco.loadAnns(annIds)
        objs = []
        for ann in anns:
            object_name = classes[ann['category_id']]
            # bbox:[x,y,w,h]
            bbox = list(map(int, ann['bbox']))
            xmin = bbox[0]
            ymin = bbox[1]
            xmax = bbox[0] + bbox[2]
            ymax = bbox[1] + bbox[3]
            obj = [object_name, xmin, ymin, xmax, ymax]
            objs.append(obj)

        file_path = os.path.join(image_path, filename)
        img = cv2.imread(file_path)
        if img is None:
            continue

        for object in objs:
            category_name = object[0]
            every_class_num[category_name] += 1
            if category_name not in category_set:
                category_id = addCatItem(category_name)
            else:
                category_id = category_set[category_name]
            xmin = int(object[1])
            ymin = int(object[2])
            xmax = int(object[3])
            ymax = int(object[4])

            if bgr:
                color = get_color_bgr(category_id)
            else:
                color = get_color_rgb(category_id)

            cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color, thickness=2)
            cv2.putText(img, category_name, (xmin, ymin), cv2.FONT_HERSHEY_SIMPLEX, 1, color, thickness=2)
            cv2.imwrite(os.path.join(imgs_save_dir, filename), img)

    # 默认统计信息
    statistics_info()
        # if show:
        #     cv2.imshow(filename, img)
        #     cv2.waitKey()
        #     cv2.destroyAllWindows()


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
        该脚本用于coco标注格式（.json）的标注框可视化
    参数明说：
        imgs-dir:图片数据路径
        anno-dir:xml标注文件路径
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
        print(every_class_num)
        print("category nums: {}".format(len(category_set)))
        print("image nums: {}".format(len(image_set)))
        print("bbox nums: {}".format(sum(every_class_num.values())))
    else:
        image_path = './data/images'
        anno_path = './data/labels/coco/train.json'
        save_img_dir = './data/save'
        draw_image(image_path, anno_path, save_img_dir)

        print(every_class_num)
        print("category nums: {}".format(len(category_set)))
        print("image nums: {}".format(len(image_set)))
        print("bbox nums: {}".format(sum(every_class_num.values())))

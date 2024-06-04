import argparse
import os
import sys
from collections import defaultdict

import cv2
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from tqdm import tqdm
import datetime

category_set = dict()
image_set = set()
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


"""
imgs_dir: 原始图片所在路径
annos_dir： 标签文件所在路径
imgs_save_dir： 绘制 bbox后的img存储位置
"""
def draw_image(imgs_dir, annos_dir, imgs_save_dir):
    assert os.path.exists(imgs_dir), "image path:{} dose not exists".format(imgs_dir)
    assert os.path.exists(annos_dir), "annotation path:{} does not exists".format(annos_dir)
    if not os.path.exists(imgs_save_dir):
        os.makedirs(imgs_save_dir)

    anno_file_list = [os.path.join(annos_dir, file) for file in os.listdir(annos_dir) if file.endswith(".txt")]
    with open(annos_dir + "/classes.txt", 'r') as f:
        classes = f.readlines()

    category_id_dict = dict((k, v.strip()) for k, v in enumerate(classes))
    for txt_file in tqdm(anno_file_list):
        if not txt_file.endswith('.txt') or 'classes' in txt_file:
            continue
        filename = txt_file.split(os.sep)[-1][:-3] + "jpg"
        image_set.add(filename)
        file_path = os.path.join(image_path, filename)
        if not os.path.exists(file_path):
            return

        img = cv2.imread(file_path)
        if img is None:
            return
        width = img.shape[1]
        height = img.shape[0]

        objects = []
        with open(txt_file, 'r') as fid:
            for line in fid.readlines():
                line = line.strip().split()
                category_name = category_id_dict[int(line[0])]
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
            xmin = int(object[1][0])
            ymin = int(object[1][1])
            xmax = int(object[1][2])
            ymax = int(object[1][3])

            def hex2rgb(h):  # rgb order (PIL)
                return tuple(int(h[1 + i:1 + i + 2], 16) for i in (0, 2, 4))

            hex = (
                'FF3838', 'FF9D97', 'FF701F', 'FFB21D', 'CFD231', '48F90A', '92CC17', '3DDB86', '1A9334', '00D4BB',
                '2C99A8', '00C2FF', '344593', '6473FF', '0018EC', '8438FF', '520085', 'CB38FF', 'FF95C8', 'FF37C7')

            palette = [hex2rgb('#' + c) for c in hex]
            n = len(palette)
            c = palette[int(category_id) % n]
            bgr = False
            color = (c[2], c[1], c[0]) if bgr else c

            cv2.rectangle(img, (xmin, ymin), (xmax, ymax), color)
            cv2.putText(img, category_name, (xmin, ymin), cv2.FONT_HERSHEY_SIMPLEX, 1, color)
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
        anno_path = './data/convert/yolo'
        save_img_dir = './data/save'

        draw_image(image_path, anno_path, save_img_dir)
        print(every_class_num)
        print("category nums: {}".format(len(category_set)))
        print("image nums: {}".format(len(image_set)))
        print("bbox nums: {}".format(sum(every_class_num.values())))

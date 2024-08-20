import cv2
import numpy as np
import os
from pathlib import Path
from utils.yamloperate import get_id_cls_dict
from tqdm import tqdm
from utils.colortable import get_color_rgb, get_color_bgr

"""
imgs_dir: 原始图片所在路径
annos_dir： 标签文件所在路径
imgs_save_dir： 绘制 bbox后的img存储位置
yaml_file: yolo 标签对应类别的文件
bgr： 颜色值格式为bgr，使用opencv绘图颜色值是bgr， 如果是rgb格式颜色值需要做相应转换
"""
def draw_image(images_dir, annos_dir, yaml_file, imgs_save_dir, bgr = True, img_type={'.jpg', '.png', '.jpeg'}):
    assert os.path.exists(images_dir), "image path:{} dose not exists".format(images_dir)
    assert os.path.exists(annos_dir), "annotation path:{} does not exists".format(annos_dir)
    if not os.path.exists(imgs_save_dir):
        os.makedirs(imgs_save_dir)

    img_id_dict = {Path(i).stem: os.path.join(images_dir, i) for i in os.listdir(images_dir) if os.path.splitext(i)[-1] in img_type}
    label_id_dict = {Path(i).stem: os.path.join(annos_dir, i) for i in os.listdir(annos_dir) if os.path.splitext(i)[-1] == '.txt'}

    id_cls_dict = get_id_cls_dict(yaml_file)
    cls_id_dict = dict((v, k) for k, v in id_cls_dict.items())

    for id in tqdm(label_id_dict.keys()):

        img_file = img_id_dict[id]
        label_file = label_id_dict[id]
        img_name = os.path.basename(img_file)
        img = cv2.imread(img_file)
        if img is None:
            return
        height, width, _ = img.shape
        objects = []
        with open(label_file, 'r') as f_r:
            for line in f_r.readlines():
                line = line.strip().split()
                objects.append(line)
        for object in objects:
            category_id = object[0]
            points = []
            x_sum = 0
            y_sum = 0
            for i in range(1, len(object), 2):
                b = [float(tmp) for tmp in object[i:i + 2]]
                x = int(b[0] * width)
                y = int(b[1] * height)
                points.append([x, y])
                x_sum += x
                y_sum += y
            center_x, center_y = x_sum/len(points), y_sum/len(points)
            if bgr:
                color = get_color_bgr(category_id)
            else:
                color = get_color_rgb(category_id)
            cv2.polylines(img, [np.array(points, np.int32)], True, color, thickness=3)
            cv2.putText(img, str(id_cls_dict[int(category_id)]), (int(center_x), int(center_y)), cv2.FONT_HERSHEY_SIMPLEX, 1, color, thickness=2)
            cv2.imwrite(os.path.join(imgs_save_dir, img_name), img)

'''
images_dir:      图片存储位置
annos_dir：      yolo 标签文件存储位置
yaml_file：      yolo 标签对应 yaml 文件
imgs_save_dir：  最终可视化后，图片保存位置
'''

if __name__ == '__main__':
    images_dir = "/home/ytusdc/Data/sdc/煤流检测/image"
    annos_dir = "/home/ytusdc/Data/sdc/煤流检测/yolo"
    yaml_file = "/home/ytusdc/codes/ultralytics/ultralytics/cfg/datasets/coco-seg-meiliu.yaml"
    imgs_save_dir = "/home/ytusdc/Data/sdc/煤流检测/result_img"
    draw_image(images_dir, annos_dir, yaml_file, imgs_save_dir)

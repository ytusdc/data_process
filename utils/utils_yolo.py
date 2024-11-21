#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-10-16 15:40
Author  : sdc
"""
import os

def xywhn2xyxy(box, size):
    """
    Args:
        box: yolo文件读到的 归一化后的 (xc, yc, wn, hn)
        size: (img_width, img_height)  , img.shape 返回的是（img_height, img_width, ch）
        这里需要注意
    Returns:
        (xmin, ymin, xmax, ymax)  左上和右下角坐标
    """
    box = list(map(float, box))
    size = list(map(float, size))
    xmin = (box[0] - box[2] / 2.) * size[0]
    ymin = (box[1] - box[3] / 2.) * size[1]
    xmax = (box[0] + box[2] / 2.) * size[0]
    ymax = (box[1] + box[3] / 2.) * size[1]
    return (xmin, ymin, xmax, ymax)

def xyxy2xywhn(bbox, size):
    """
    Args:
        bbox: (xmin, ymin, xmax, ymax)
        size:  (img_width, img_height)， img.shape 返回的是（img_height, img_width, ch）
        这里需要注意
    Returns:
       归一化后的  (xc, yc, wn, hn)
    """
    bbox = list(map(float, bbox))
    size = list(map(float, size))
    xc = (bbox[0] + (bbox[2] - bbox[0]) / 2.) / size[0]
    yc = (bbox[1] + (bbox[3] - bbox[1]) / 2.) / size[1]
    wn = (bbox[2] - bbox[0]) / size[0]
    hn = (bbox[3] - bbox[1]) / size[1]
    return (xc, yc, wn, hn)


def xywhn2xywh(bbox, size):
    """
    Args:
        bbox: yolo文件读到的 归一化后的 (xc, yc, wn, hn)
        size: (img_width, img_height)  , img.shape 返回的是（img_height, img_width, ch）
        这里需要注意
    """
    bbox = list(map(float, bbox))
    size = list(map(float, size))
    xmin = (bbox[0] - bbox[2] / 2.) * size[0]
    ymin = (bbox[1] - bbox[3] / 2.) * size[1]
    w = bbox[2] * size[0]
    h = bbox[3] * size[1]
    box = (xmin, ymin, w, h)
    return list(map(int, box))

def parse_yolo(label_file, shape):
    """
    Args:
        label_file:
        shape: opencv 获取的图片尺寸shape， [height, width, depth]
    Returns:
    objects = [object1, object2]
    object = [category_id, (xmin, ymin, xmax, ymax)]
    """
    img_height = shape[0]
    img_width = shape[1]
    objects = []
    with open(label_file, 'r') as f_d:
        for line in f_d.readlines():
            line = line.strip().split()
            category_id = str(line[0])
            bbox = xywhn2xyxy((line[1], line[2], line[3], line[4]), (img_width, img_height))
            obj = [category_id, bbox]
            objects.append(obj)
    return objects
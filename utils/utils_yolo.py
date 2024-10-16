#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-10-16 15:40
Author  : sdc
"""
import os

def xywhn2xyxy(box, size):
    box = list(map(float, box))
    size = list(map(float, size))
    xmin = (box[0] - box[2] / 2.) * size[0]
    ymin = (box[1] - box[3] / 2.) * size[1]
    xmax = (box[0] + box[2] / 2.) * size[0]
    ymax = (box[1] + box[3] / 2.) * size[1]
    return (xmin, ymin, xmax, ymax)

def parse_yolo(label_file, img_height, img_width):
    objects = []
    with open(label_file, 'r') as f_d:
        for line in f_d.readlines():
            line = line.strip().split()
            category_id = str(line[0])
            bbox = xywhn2xyxy((line[1], line[2], line[3], line[4]), (img_width, img_height))
            obj = [category_id, bbox]
            objects.append(obj)
    return objects
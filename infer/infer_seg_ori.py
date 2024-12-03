#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import cv2
import numpy as np
from pathlib import Path
import argparse
import yaml
from tqdm import tqdm

class OpencvSeg:
    def __init__(self, modelpath):
        self.classes = ['background', 'coal']
        self.net = cv2.dnn.readNet(modelpath)
        self.size = 480

    def predict(self, frame):
        from_height, from_width, _ = frame.shape
        to_height, to_width = self.size, self.size

        scale_x = to_width / from_width
        scale_y = to_height / from_height

        scale = min(scale_x, scale_y)
        ox = (-scale * from_width + to_width + scale - 1) * 0.5
        oy = (-scale * from_height + to_height + scale - 1) * 0.5
        k = 1 / scale

        i2d = np.array([[scale, 0, ox], [0, scale, oy]])
        d2i = np.array([[k, 0, -k * ox], [0, k, -k * oy]])

        input_image = cv2.warpAffine(frame, i2d, (to_width, to_height))
        blob = cv2.dnn.blobFromImage(input_image, 1 / 255.0, (self.size, self.size), [0, 0, 0], swapRB=True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.net.getUnconnectedOutLayersNames())
        out = outs[0][0]

        mask = np.zeros((self.size, self.size, 3))
        mask[out[0] < out[1]] = [0, 0, 255]
        mask_ = cv2.warpAffine(mask, d2i, (from_width, from_height)).astype(np.uint8)
        blended = cv2.addWeighted(frame, 0.7, mask_, 0.3, 0)
        return blended


# 煤流测试
def coal_video():
    model_path = "/home/ytusdc/codes_zkyc/svn_Release/源模型/语义分割/皮带状态/煤流检测_v2.onnx"
    model = OpencvSeg(model_path)  # 模型
    videopath = "/home/ytusdc/测试数据/9号皮带/20230220/22/ch22_20230220182404.mp4"
    savepath = "/home/ytusdc/测试数据/9号皮带/20230220/coal_result_video"

    path1, filename = os.path.split(videopath)
    savepath1 = os.path.join(savepath, filename[:-4])
    Path(savepath1).mkdir(parents=True, exist_ok=True)
    # if not os.path.exists(savepath1):
    #     os.mkdir(savepath1)

    num = 1000
    cap = cv2.VideoCapture(videopath)
    cv2.namedWindow("out", 0)
    count_frame = 0
    while True:
        ret, frame = cap.read()
        if (ret == 0):
            break
        if ret:
            result = model.predict(frame)
            formatted_name = str(count_frame).zfill(6) + ".jpg"
            save_file = os.path.join(savepath1, formatted_name)
            cv2.imwrite(save_file, result)


            # cv2.imencode('.jpg', result)[1].tofile(savepath1 + "/" + str(count_frame) + ".jpg")


            cv2.imshow('out', result)
            cv2.waitKey(1)

            count_frame += 1


def coal_images():
    model_path = "/home/ytusdc/codes_zkyc/svn_Release/源模型/语义分割/皮带状态/煤流检测_v2.onnx"
    model = OpencvSeg(model_path)  # 模型
    imagepath = "/home/ytusdc/测试数据/9号皮带/20230220/ch22_20230221175218"  # 测试的图片文件夹
    savepath = "/home/ytusdc/测试数据/9号皮带/20230220/coal_result"  # 测试结果存放路径
    if not os.path.exists(savepath):
        os.makedirs(savepath)

    imglist = os.listdir(imagepath)
    cv2.namedWindow("1", 0)
    for im in imglist:
        impath = os.path.join(imagepath, im)
        # img = cv2.imread(impath)
        img = cv2.imdecode(np.fromfile(impath, dtype=np.uint8), 1)
        if img is None:
            continue
        result = model.predict(img)
        cv2.imencode('.jpg', result)[1].tofile(os.path.join(savepath, im))

        cv2.imshow("1", result)
        cv2.waitKey(1)

    cv2.destroyAllWindows()


def main():
    pass

if __name__ == "__main__":
    coal_video()
    # coal_images()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from logger import logger
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import cv2


class Template:
    def __init__(self):
        self.alarm_result = {"is_alarm": False, "alarm_type": "", "alarm_data": "", "alarm_boxes": []}
        self.count_PIL = 0
        self.count_cv2 = 0
        self.count = 0

    def process(self, params):
        tmp_result = self.alarm_result.copy()
        addr = params.get("addr", None)
        im = params.get("im", None)
        det = params.get("det", [])

        # self.write_img_PIL(im, det)
        # self.write_img_cv2(im, det)

        if addr is not None and im is not None and len(det) > 0:
            tmp_result["is_alarm"] = True
            tmp_result["alarm_boxes"] = det

            # img_name = "img_" + str(self.count) + ".jpg"
            # image_array = im.astype(np.uint8)
            # img = Image.fromarray(image_array)
            # save_img = os.path.join(save_dir, img_name)
            # img.save(save_img)

            self.write_img_PIL(im, det)
            self.write_img_cv2(im, det)

            self.write_test(tmp_result)

        else:
            # if im is not None:
            #     img_name = "img_no_det_" + str(self.count) + ".jpg"
            #     image_array = im.astype(np.uint8)
            #     img = Image.fromarray(image_array)
            #     save_img = os.path.join(save_dir, img_name)
            #     img.save(save_img)
            #     self.count += 1
            self.write_empty(tmp_result)
            pass

        # logger.info(str(tmp_result))
        return tmp_result

    def write_test(self, result_info):
        # result_info = self.alarm_result.copy()
        # file_path = r"/home/ytusdc/log_1.txt"
        file_path = "/root/log.txt"
        with open(file_path, 'a') as f_w:
            str_write = str(result_info)
            f_w.write(str_write + "\n")

    def write_empty(self, info):
        file_path = "/root/log_empty.txt"
        with open(file_path, 'a') as f_w:
            str_write = str(info)
            f_w.write(str_write + "\n")

    def write_img_PIL(self, img_data, det_boxs):

        save_dir = "/root/save_img_PIL"
        # save_dir = "/home/ytusdc/save_img_PIL"
        if not Path(save_dir).exists():
            Path(save_dir).mkdir(parents=True, exist_ok=True)
        image_data = img_data.astype(np.uint8)
        img = Image.fromarray(image_data)

        draw = ImageDraw.Draw(img)
        for det_box in det_boxs:
            x1, y1, x2, y2, score, text = det_box
            rectangle_shape = (x1, y1, x2, y2)
            rectangle_color = 'green'  # 矩形颜色
            draw.rectangle(rectangle_shape, outline=rectangle_color, width=3)

            # font = ImageFont.load_default()  # 如果指定字体文件不存在，则使用默认字体
            # text_color = 'blue'
            # # text_color = (0, 255, 0)
            # text_position = (x1, y1 + 40)  # 文字位置，相对于矩形框调整
            # draw.text(text_position, text, fill=text_color, font=font)

        img_name = "img_" + str(self.count_PIL) + ".jpg"
        save_img = os.path.join(save_dir, img_name)
        img.save(save_img)
        self.count_PIL += 1

    def write_img_cv2(self, img_data, det_boxs):
        save_dir = "/root/save_img_cv2"
        # save_dir = "/home/ytusdc/save_img_cv2"
        if not Path(save_dir).exists():
            Path(save_dir).mkdir(parents=True, exist_ok=True)

        image_data = img_data.astype(np.uint8)

        for det_box in det_boxs:

            x1, y1, x2, y2, score, text = det_box
            color = (0, 255, 0)  # 矩形框颜色(B,G,R)
            thickness = 2  # 矩形框线条粗细
            # 在图像上绘制矩形框
            cv2.rectangle(image_data, (x1, y1), (x2, y2), color, thickness)
            text_origin = (x1, y1 + 20)

            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1
            text_color = (255, 0, 0)  # 文字颜色(B,G,R)
            line_type = 2  # 线条类型
            cv2.putText(image_data, text, text_origin, font, font_scale, text_color, line_type)

        img_name = "img_" + str(self.count_cv2) + ".jpg"
        save_img = os.path.join(save_dir, img_name)
        cv2.imwrite(save_img, image_data)

        self.count_cv2 += 1


# if __name__ == '__main__':
#     tttt = Template()
#     param = {}
#
#     im = np.random.randint(0, 256, size=(1920, 1080), dtype=np.uint8)
#     det = [[621, 165, 724, 442, 0.9707307815551758, 'person']]
#
#     param['im'] = im
#     param['det'] = det
#
#     tttt.process(param)
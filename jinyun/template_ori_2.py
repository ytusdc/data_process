# -*-coding:utf-8-*-
import os
import uuid
import base64
from datetime import datetime
import requests
import sys
sys.path.append('/root/service')

from flask import Flask, Response
import multiprocessing as mp
from multiprocessing import Process
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

from obs import PutObjectHeader
from obs import ObsClient
from logger import logger


class PushStream(Process):
    def __init__(self, flask_queue, addr):
        addrs = os.getenv('ADDRS').split(',')
        for idx, a in enumerate(addrs):
            if addr == a:
                self.index = str(idx + 1)
                self.port = 8008 + idx
        self.flask_queue = flask_queue
        self.app = Flask(__name__)
        self.app.add_url_rule("/person" + self.index, "person" + self.index, view_func=self.route, methods=["GET"])
        super(PushStream, self).__init__()

    def video_feed(self):
        while True:
            img = self.flask_queue.get()
            ret, jpeg = cv2.imencode('.jpg', img)
            if jpeg is not None:
                self.global_frame = jpeg.tobytes()
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + self.global_frame + b'\r\n\r\n')
            else:
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + self.global_frame + b'\r\n\r\n')

    def route(self):
        return Response(self.video_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

    def run(self):
        self.app.run(host='0.0.0.0', port=self.port)

    def set_daemon(self, flag):
        self.daemon = flag


class PushWarning(Process):

    def __init__(self, params_queue, flask_queue, last_alarm_time='2000-01-01 00:00:00'):
        self.warning_state = False
        self.warning_list = []
        self.params_queue = params_queue
        self.flask_queue = flask_queue
        self.last_alarm_time = datetime.strptime(last_alarm_time, "%Y-%m-%d %H:%M:%S")
        self.ALARM_DEGREE_MAP = {}
        self.ALARM_PREVIOUS = [0, 0, 0]

        if os.getenv('ADDRS', None):
            for index, addr in enumerate(os.getenv('ADDRS', None).split(',')):
                self.ALARM_DEGREE_MAP[addr] = index

            print('ALARM_DEGREE_MAP:', self.ALARM_DEGREE_MAP)
        super(PushWarning, self).__init__()

    def run(self):
        while True:
            params = self.params_queue.get()
            frame = self.bj_logic(params)
            print('param addr:', params.get('addr'))
            self.put_flask_queue(frame)

    def put_flask_queue(self, img):
        self.flask_queue.put(img)

        if self.flask_queue.qsize() > 5:
            self.flask_queue.get()

    def get_token(self):
        url = "http://192.168.16.222:8090/oauth/accessToken"
        header = {"appKey": '71m7ea3tnaiiggqpn', "appSecret": '_Qd0HUb^'}
        response = requests.post(url, json=header, verify=False, timeout=10)

        if response.json()['success']:
            return response.json()['result']
        else:
            print('get token error, error code', response.text['code'])
            return None

    def im_to_base64(self, img):
        base64_str = cv2.imencode('.jpg', img)[1].tobytes()
        data = "data:image/jpg;base64," + base64.b64encode(base64_str).decode()
        return data

    def bj_img(self, im, addr, im_draw):
        warningUrl = "http://192.168.16.222:8090/aiAlarm/saveHwAlarm"
        now = datetime.now()
        onlineTime = now.strftime("%Y-%m-%d %H:%M:%S")
        if (datetime.strptime(onlineTime, "%Y-%m-%d %H:%M:%S") - self.last_alarm_time).seconds < \
                float(os.getenv('ALARM_INTERVAL', 15)):
            logger.info('距离上次告警发送时间不足15秒，本次告警不上传！')
            return
        self.last_alarm_time = datetime.strptime(onlineTime, "%Y-%m-%d %H:%M:%S")

        addr_index = int(self.ALARM_DEGREE_MAP[addr])

        if os.getenv('ALARM_DEDREE_LIST'):
            DEGREE = str(os.getenv('ALARM_DEDREE_LIST').split(',')[addr_index])
        else:
            DEGREE = '2'

        payload = {
            "modelId": os.getenv('MODEL_ID', 'cadb7588-59ad-4bb8-b064-81f4539a16c8'),
            "deviceId": os.getenv('DEVICE_ID', 'jiezhitonglilou001').split(',')[addr_index],
            "alarmNo": str(uuid.uuid4()),
            "picture": self.im_to_base64(im),
            "markedPicture": self.im_to_base64(im_draw),
            "alarmContent": "人员入侵",
            "time": onlineTime,
            "eventInfo": DEGREE}
        token = self.get_token()
        headers = {'X-Access-Token': token}
        response = requests.request("POST", warningUrl, headers=headers, json=payload, timeout=3)
        result = response.text.encode("utf-8")
        print('告警返回结果：', result)

    def bj_logic(self, params):
        addr = params.get("addr", None)
        im = params.get("im", None)
        dets = params.get("det", [])
        im_draw = self.draw_result(im, dets)
        if dets:
            self.ALARM_PREVIOUS.pop(0)
            self.ALARM_PREVIOUS.append(1)
        else:
            self.ALARM_PREVIOUS.pop(0)
            self.ALARM_PREVIOUS.append(0)

        if all(self.ALARM_PREVIOUS):
            self.bj_img(im, addr, im_draw)

        return im_draw

    def draw_result(self, img, dets):
        if not dets:
            resized_img = cv2.resize(img, (540, 360))
            return resized_img

        images = Image.fromarray(img)
        draw = ImageDraw.Draw(images)
        font = ImageFont.truetype(font='./obs_template/simsun.ttf', size=np.floor(3e-2 * 1500 + 0.5).astype('int32'))
        for det in dets:
            label = '{}_{}%'.format('人', int(det[4] * 100))
            bbox = [int(float(ele)) for ele in det[0:4]]
            label_bbox = draw.textbbox([0, 0], label, font=font)
            postion_label = [bbox[0], bbox[1] - label_bbox[3]]
            draw.rectangle(((bbox[0], bbox[1]), (bbox[2], bbox[3])), fill=None, outline=(0, 255, 0), width=5)
            draw.rectangle(((bbox[0], bbox[1] - (label_bbox[3] - label_bbox[1])),
                            (bbox[0] + label_bbox[2], bbox[1])), fill=(0, 255, 0), outline=(0, 255, 0), width=0)
            label = label.encode('utf-8')
            draw.text(postion_label, label.decode(), fill='white', font=font)

        img = np.asarray(images)
        resized_img = cv2.resize(img, (540, 360))

        return resized_img

    def set_daemon(self, flag):
        self.daemon = flag


class Template(object):
    def __init__(self):

        # warning
        self.alarm_result = {"is_alarm": False, "alarm_type": "", "alarm_data": ""}
        self.params_queue = mp.Queue(maxsize=0)
        self.flask_queue = mp.Queue(maxsize=0)

        self.push_warning = PushWarning(self.params_queue, self.flask_queue)
        self.push_warning.set_daemon(True)
        self.push_warning.start()

        self.init_push = False


    def det_filter(self, dets):
        if not isinstance(dets, list) or len(dets) == 0:
            return dets
        results = []
        for x1, y1, x2, y2, score, name in dets:
            if score < float(os.getenv(name + '_thresh')):
                continue
            results.append([x1, y1, x2, y2, score, name])
        return results

    def process(self, params):
        if not self.init_push:
            self.push_stream = PushStream(self.flask_queue, params.get("addr"))
            self.push_stream.set_daemon(True)
            self.push_stream.start()
            self.init_push = True
        print('raw det:', params.get('det'))
        params['det'] = self.det_filter(params.get('det'))
        print('filter det:', params.get('det'))
        if self.params_queue.qsize() > 5:
            self.params_queue.get()
        self.params_queue.put(params)
        return self.alarm_result


if __name__ == '__main__':
    import numpy as np
    import time

    temp = Template()
    for i in range(10000):
        print(i)
        time.sleep(0.1)
        im = np.ones((500, 500, 3)) * (i % 100) + 150
        im = im.astype(np.uint8)
        if i % 2 == 0:
            tmp_data = {"det": [[100, 100, 400, 400, 0.9, 'person'],
                                [200, 200, 350, 350, 0.93, 'person']], "im": im,
                        'addr': 'rtsp://admin:Xlz091105@@10.91.38.20:554/Streaming/Channels/2401'}
        else:
            tmp_data = {"det": [[100, 100, 400, 400, 0.9, 'person']], "im": im,
                        'addr': 'rtsp://admin:Xlz091105@@10.91.38.20:554/Streaming/Channels/2601'}

        temp.process(tmp_data)
    while True:
        pass









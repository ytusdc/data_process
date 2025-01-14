#!/usr/bin/env python
# -*- coding: utf-8 -*-
from logger import logger
class Template:
    def __init__(self):
        self.alarm_result = {"is_alarm": False, "alarm_type": "", "alarm_data": "", "alarm_boxes": []}

    def process(self, params):
        tmp_result = self.alarm_result.copy()
        addr = params.get("addr", None)
        im = params.get("im", None)
        det = params.get("det", [])
        if addr is not None and im is not None and len(det) > 0:
            tmp_result["is_alarm"] = True
            tmp_result["alarm_boxes"] = det
        logger.info(str(tmp_result))
        return tmp_result
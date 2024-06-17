#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pathlib import Path

re = (None or 10)

txt_file = "/home/ytusdc/paper/ori_txt.txt"

line_result = []
with open(txt_file, 'r') as f_r:
    lines = f_r.readlines()
    for line in lines:
        if line.strip() == '':
            continue
        else:
            line_result.append(line.strip() + "\n")

save_txt_file = "/home/ytusdc/paper/save.txt"
with open(save_txt_file, 'w') as f_w:
    for line in line_result:
        f_w.write(line)
        f_w.write("\n")


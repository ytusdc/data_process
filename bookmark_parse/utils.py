#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Time    : 2024-10-11 15:16
Author  : sdc
"""
def print_with_style_and_color(text, color=None, style=None):

    # 定义风格代码
    styles_dict = {
        'reset': '0',     #默认重置字体
        'bold': '1',      #加粗
        'underline': '4', #下划线
        'italic': '3',    #斜体
        'reverse': '7'    #背景反白
    }

    # 定义颜色代码
    colors_dict = {
        'reset': '0',   # 默认重置字体所有属性, 会覆盖styles的属性
        'black': '30',
        'red': '31',
        'green': '32',
        'yellow': '33',
        'blue': '34',
        'magenta': '35',
        'cyan': '36',
        'white': '37'
    }

    # 获取风格代码
    style_code = styles_dict.get(style, '0')    # 找不到相应key, 默认重置
    # 获取颜色代码
    color_code = colors_dict.get(color, '0')    # 找不到相应key，默认重置

    """
    '\033[{style_code};{color_code}m{text}\033[0m'
    输出带有颜色和字体的文字， 可能由于顺序原因 color_code 的优先级大于 style_code，
    当 color_code 为 ‘reset’ 时，会重置所有字体到默认输出状态，因此分别判断输出
    """
    if color is None and style is None:
        print(f'{text}')  # 原始输出
    elif color is None and style is not None:
        print(f'\033[{style_code}m{text}\033[0m')  # 只修改字体输出
    elif color is not None and style is None:
        print(f'\033[{color_code}m{text}\033[0m')  # 只修改颜色输出
    elif color is not None and style is not None:
        print(f'\033[{style_code};{color_code}m{text}\033[0m')  # 输出带风格和颜色的文字
'''
# opencv 颜色默认是 BGR, 使用opencv 绘图需要做相应变化
bgr = True
color_bgr = (color_rgb[2], color_rgb[1], color_rgb[0]) if bgr else color_rgb
'''

# 下面颜色值是 RGB 顺序
color_rgb_ls = [
    (0, 255, 0),      #绿色
    (255, 128, 0),    #橘黄
    (255, 192, 203),  #粉红
    (0, 0, 255),      #蓝色
    (255, 255, 0),    #黄色
    (255, 0, 255),    #深红
    (0, 255, 255),    #青色
    (176, 23, 1),     #印度红
    (153, 51, 250),   #紫色
    (0, 199, 140),    #锰蓝
    (255, 0, 0),  # 红色
]

# 16 进制颜色值
hex = (
    'FF3838', 'FF9D97', 'FF701F', 'FFB21D', 'CFD231', '48F90A', '92CC17', '3DDB86', '1A9334', '00D4BB',
    '2C99A8', '00C2FF', '344593', '6473FF', '0018EC', '8438FF', '520085', 'CB38FF', 'FF95C8', 'FF37C7')

def hex2rgb_ls():
# 16进制 转 rgb 颜色值
    def hex2rgb(h):  # rgb order (PIL)
        return tuple(int(h[1 + i:1 + i + 2], 16) for i in (0, 2, 4))
    rgb_ls = [hex2rgb('#' + c) for c in hex]
    return rgb_ls

def get_color_rgb(category_id):
     n = len(color_rgb_ls)
     color_rgb = color_rgb_ls[int(category_id) % n]
     return color_rgb

def get_color_bgr(category_id):
    n = len(color_rgb_ls)
    color_rgb = color_rgb_ls[int(category_id) % n]
    return rgb2bgr(color_rgb)

def rgb2bgr(color_rgb):
    color_bgr = (color_rgb[2], color_rgb[1], color_rgb[0])
    return color_bgr



from PIL import Image
from utils import *

def is_png(file_path):
    try:
        # 打开图像文件
        with Image.open(file_path) as img:
            # 检查图像格式是否为 PNG
            return img.format == 'PNG'
    except Exception as e:
        print(f"无法打开或识别文件: {e}")
        return False

# 示例用法
file_path = '/home/ytusdc/frame_0003.png'  # 替换为您的文件路径
if is_png(file_path):
    print("这是一个真正的 PNG 文件")
else:
    print("这不是一个真正的 PNG 文件")
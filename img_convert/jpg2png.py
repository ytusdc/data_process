from PIL import Image
from utils import common




def jpg_to_png(input_path, output_path):
    try:
        # 打开 JPG 图像
        img = Image.open(input_path)

        # 保存为 PNG 格式
        img.save(output_path, 'PNG')
        print(f"成功将 {input_path} 转换为 {output_path}")
    except Exception as e:
        print(f"转换失败: {e}")


path_dir = "/home/ytusdc/test_seg"

file_ls = common.get_filepath_ls(path_dir)


for file in file_ls:
    input_file = file
    out_file = file.replace(".jpg", ".png")
# 示例用法
    jpg_to_png(input_file, out_file)  # 替换为您的文件路径
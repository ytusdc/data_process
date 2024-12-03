import cv2
import os
import subprocess
from tqdm import tqdm
from pathlib import Path

"""
(wxh)                  radio
(1280x720像) : 720P,   1.77
(1920*1080) : 1080P.   1.77
(2560*1440) : 2k,      1.77
(3840*2160) : 4K,      1.31
"""

def images_to_video(image_folder, video_path, fps, size=None):
    # 获取图片列表
    images = [img for img in os.listdir(image_folder) if img.endswith(".png") or img.endswith(".jpg")]
    images.sort()  # 确保图片按顺序排列

    # 读取第一张图片以获取视频的宽度和高度
    if size is None:
        frame = cv2.imread(os.path.join(image_folder, images[0]))
        height, width, layers = frame.shape
        size = (width, height)

    #编码参数：
    # cv2.VideoWriter_fourcc('M', 'P', '4', 'V') MPEG-4编码 .mp4  要限制结果视频的大小，这是一个很好的选择。
    # cv2.VideoWriter_fourcc('X','2','6','4')   MPEG-4编码  .mp4  想限制结果视频的大小，这可能是最好的选择。
    # cv2.VideoWriter_fourcc('I', '4', '2', '0'),该参数是YUV编码类型，文件名后缀为.avi   广泛兼容，但会产生大文件
    # cv2.VideoWriter_fourcc('P', 'I', 'M', 'I'),该参数是MPEG-1编码类型，文件名后缀为.avi
    # cv2.VideoWriter_fourcc('X', 'V', 'I', 'D'),该参数是MPEG-4编码类型，文件名后缀为.avi  要限制结果视频的大小，这是一个很好的选择。
    # cv2.VideoWriter_fourcc('T', 'H', 'E', 'O'),该参数是Ogg Vorbis,文件名后缀为.ogv
    # cv2.VideoWriter_fourcc('F', 'L', 'V', '1'),该参数是Flash视频，文件名后缀为.flv
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')    # 使用 MPEG-4 视频编解码器, .mp4
    # fourcc = cv2.VideoWriter_fourcc(*'X264')  # 使用 H.264 编解码器
    # fourcc = cv2.VideoWriter_fourcc(*'avc1')  # 使用 H.264 编解码器 (AVC)
    # fourcc = cv2.VideoWriter_fourcc(*'XVID')
    # fourcc = cv2.VideoWriter_fourcc(*'X','2','6','4')

    # 创建视频写入对象
    video_write = cv2.VideoWriter(video_path, fourcc, fps, size)
    # 写入每一帧图片
    for image in tqdm(images):
        img_np = cv2.imread(os.path.join(image_folder, image))
        resize_img = cv2.resize(img_np, size, interpolation=cv2.INTER_NEAREST)
        video_write.write(resize_img)
    # 释放视频写入对象
    video_write.release()

def compress_video(video_path):
    # 可选：使用 ffmpeg 进行进一步压缩
    save_dir = str(Path(video_path).parent)
    name =  Path(video_path).stem
    suffix = Path(video_path).suffix
    commpress_video_name = name + "_compressed" + suffix

    ffmpeg_command = [
        'ffmpeg',
        '-i', video_path,
        '-vcodec', 'libx264',
        '-crf', '23',
        '-preset', 'veryfast',
        os.path.join(save_dir, commpress_video_name)
    ]
    subprocess.run(ffmpeg_command)
    print("Further compression using ffmpeg completed.")


def main():
    image_folder = '/home/ytusdc/测试数据/10.11/20241010000825-20241010110825/result/output_segment_2'
    video_path = '/home/ytusdc/测试数据/10.11/20241010000825-20241010110825/result/result.mp4'
    fps = 25  # 每秒帧数
    video_size = None
    video_size = (1920, 1080)

    images_to_video(image_folder, video_path, fps, size=video_size)
    compress_video(video_path)


if __name__ == "__main__":
    main()


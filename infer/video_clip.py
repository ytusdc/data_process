import os
from pathlib import Path
import cv2


def str2senond(str_time):
    """
    Args:
        str_time: str_time format is hh:mm:ss
    """
    split_ls = str_time.strip().split(":")
    for i in split_ls:
        if not i.isnumeric():
            print(f"输入的时间中包含，非数字，{str_time}")
            return -1

    if len(split_ls) == 1:
        if int(str_time) >= 60:
            print(f"秒不能大于60，当前秒输入是： {str_time}")
            return -1
        return int(str_time)
    elif len(split_ls) == 2:
        m, s = split_ls
        if int(m) >= 60 or int(m) >= 60:
            print(f"分钟和秒不能大于60，当前秒输入是, {m}:{s}")
            return -1
        return  int(m) * 60 + int(s)
    elif len(split_ls) == 3:
        h, m, s = str_time.strip().split(":")
        if int(m) >= 60 or int(m) >= 60:
            print(f"分钟和秒不能大于60，当前秒输入是, {m}:{s}")
            return -1
        return int(h) * 3600 + int(m) * 60 + int(s)
    else:
         return -1

def extract_video_segment(video_path, clip_video_path, start_time, end_time):
    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    # 获取视频属性
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"FPS: {fps}, Width: {width}, Height: {height}")

    start_seconds = str2senond(start_time)
    end_seconds = str2senond(end_time)
    if start_seconds == -1 or end_seconds==-1:
        print("时间转换有问题，情检查时间格式是否输入正确")
        return
    # 指定开始和结束时间（秒）
    start_frame = int(start_seconds * fps)
    end_frame = int(end_seconds * fps)

    # 设置视频读取位置到开始帧
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    # 创建一个VideoWriter对象来保存输出视频
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # 或者使用其他编码格式如 'mp4v'
    out = cv2.VideoWriter(clip_video_path, fourcc, fps, (width, height))

    frame_index = start_frame
    while cap.isOpened() and frame_index <= end_frame:
        ret, frame = cap.read()
        if not ret:
            print("End of video or error reading frame.")
            break

        out.write(frame)  # 写入帧到输出视频
        frame_index += 1

        # 可选：显示处理进度
        if frame_index % 100 == 0:
            print(f"Processing frame {frame_index}/{end_frame}")

    # 释放资源
    cap.release()
    out.release()
    print("Extraction complete.")



if __name__ == '__main__':

    input_video_path = '/home/ytusdc/测试数据/10.11/20241010000825-20241010110825/路卡下_采选路卡_采选路卡，100.142_20241007125829_20241007151951_3219837.mp4'  # 输入视频路径
    output_video_path = '/home/ytusdc/测试数据/10.11/20241010000825-20241010110825/output_segment_2.avi'  # 输出视频路径
    start_time = "0:45:20"  # 开始时间为5秒
    end_time = "0:50:00"   # 结束时间为10秒


    extract_video_segment(input_video_path, output_video_path, start_time, end_time)
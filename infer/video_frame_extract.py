import os
from pathlib import Path
import cv2
import datetime

from rope.base.oi.type_hinting.evaluate import prefix


def str2second(str_time):
    """
    Args:
        str_time: str_time format is hh:mm:ss
        输入格式：hh:mm:ss / mm:ss / ss
    """
    split_ls = str_time.strip().split(":")
    for i in split_ls:
        if not i.isnumeric():
            print(f"输入的时间中包含，非数字，{str_time}")
            return -1
    # ss
    if len(split_ls) == 1:
        if int(str_time) >= 60:
            print(f"秒不能大于60，当前秒输入是： {str_time}")
            return -1
        return int(str_time)
    # mm:ss
    elif len(split_ls) == 2:
        m, s = split_ls
        if int(m) >= 60 or int(m) >= 60:
            print(f"分钟和秒不能大于60，当前秒输入是, {m}:{s}")
            return -1
        return  int(m) * 60 + int(s)
    # hh:mm:ss
    elif len(split_ls) == 3:
        h, m, s = str_time.strip().split(":")
        if int(m) >= 60 or int(m) >= 60:
            print(f"分钟和秒不能大于60，当前秒输入是, {m}:{s}")
            return -1
        return int(h) * 3600 + int(m) * 60 + int(s)
    else:
         return -1

def get_video_attribute(video_cap):
    # 获取视频属性
    fps = video_cap.get(cv2.CAP_PROP_FPS)
    width = int(video_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # # 获取视频总帧数
    frame_count = int(video_cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"FPS: {fps}, Width: {width}, Height: {height}， 总帧数： {frame_count}")

def traverse_folder(folder_path, suffix=None):
    if suffix is None:
        suffix = (".mp4", ".avi")

    if Path(folder_path).is_file() and folder_path.endswith(suffix):
        return [folder_path]   # 如果传入的是视频文件，则直接返回

    file_path_ls = []
    for file_path in Path(folder_path).glob('**/*'):
        if file_path.is_file() and str(file_path).endswith(suffix):
            # print(file_path)
            file_path_ls.append(str(file_path))
    return file_path_ls

def clip_video_segment(video_path, clip_video_path, start_time, end_time):
    """
    视频截取某一段
    Args:
        video_path:      原始 video 存储路径
        clip_video_path: 截取的 video 存储路径
        start_time: 截取的开始时间
        end_time:   截取的结束时间
    Returns:
    """
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

    start_seconds = str2second(start_time)
    end_seconds = str2second(end_time)
    if start_seconds == -1 or end_seconds==-1:
        print("时间转换有问题，情检查时间格式是否输入正确")
        return
    # 指定开始和结束时间（秒）
    start_frame = int(start_seconds * fps)
    end_frame = int(end_seconds * fps)

    # 创建一个VideoWriter对象来保存输出视频
    fourcc = cv2.VideoWriter_fourcc(*'XVID')  # 或者使用其他编码格式如 'mp4v'
    video_write = cv2.VideoWriter(clip_video_path, fourcc, fps, (width, height))

    # 设置视频读取位置到开始帧
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    frame_index = start_frame
    while cap.isOpened() and frame_index <= end_frame:
        ret, frame = cap.read()
        if not ret:
            print("End of video or error reading frame.")
            break
        video_write.write(frame)  # 写入帧到输出视频
        frame_index += 1

        # 显示处理进度
        if frame_index % 100 == 0:
            print(f"Processing frame {frame_index}/{end_frame}")
    # 释放资源
    cap.release()
    video_write.release()
    print("Extraction complete.")


def extract_frame(video_path_dir, save_dir, interval=10, prefix=None):
    '''
    视频抽帧
    Args:
        video_path_dir:  视频video路径, 或者视频video文件夹
        save_dir:    抽帧图片保存路径
        interval: 间隔 interval 帧保存图片
        prefix:   抽取frame保存的前缀
    Returns:
    '''

    # 获取当前日期时间
    now = datetime.datetime.now()
    # 格式化日期时间字符串
    # datetime_str = now.strftime("%Y%m%d%H%M%S")
    datetime_str = now.strftime("%Y%m%d")

    if prefix is None:
        prefix = datetime_str
    elif isinstance(prefix, str) and prefix.strip() == "":
        prefix = datetime_str
    else:
        prefix = str(prefix).strip() + "_" + datetime_str

    Path(save_dir).mkdir(parents=True, exist_ok=True)

    video_path_ls = traverse_folder(video_path_dir)

    count_frame = 0
    for video_path in video_path_ls:
        # 创建视频捕获对象, 创建一个VideoCapture对象，参数是视频文件的路径
        cap = cv2.VideoCapture(video_path)  # 替换为你的视频文件路径
        # 检查视频是否打开成功
        if not cap.isOpened():
            print(f"Error: Could not open video: {video_path}")
            continue
        get_video_attribute(cap)
        while True:
            ret, frame = cap.read()  # 读取一帧
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break

            if count_frame % interval == 0:
                formatted_name = prefix + "_" + str(int(count_frame / interval)).zfill(6) + ".jpg"
                # formatted_name = str(count_frame).zfill(6) + ".jpg"
                img_save_path = os.path.join(save_dir, formatted_name)
                cv2.imwrite(str(img_save_path), frame)
            count_frame += 1

        # 释放捕获对象
        cap.release()

def video_clip_segment():
    input_video_path = '/home/ytusdc/测试数据/01000000772000000.mp4'  # 输入视频路径
    output_video_path = '/home/ytusdc/测试数据/01000000772000000_clip_no.mp4'  # 输出视频路径
    start_time = "2:09:0"  # 开始时间: hh:mm:ss / mm:ss / ss
    end_time = "2:14:0"   # 结束时间：hh:mm:ss / mm:ss / ss

    clip_video_segment(input_video_path, output_video_path, start_time, end_time)

def video_extract():
    video_path = "/home/ytusdc/测试数据/车辆/192.168.10.123/00000000065000000.mp4"
    save_dir  = "/home/ytusdc/测试数据/车辆/192.168.10.123/extract_frame"
    interval = 25
    extract_frame(video_path, save_dir, interval)

if __name__ == '__main__':
    video_extract()
    # video_clip_segment()
    print("")



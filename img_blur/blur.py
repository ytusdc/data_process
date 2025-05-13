import os
from pathlib import Path
import cv2
import numpy as np


'''
1. 基于Laplacian方差的清晰度检测
这种方法通过计算图像经过Laplacian变换后的方差来衡量图像的清晰度。方差越大，说明图像越清晰

原理，Laplacian算法。偏暗的图片，二阶导数小，区域变化小；偏亮的图片，二阶导数大，区域变化快。

拉普拉斯变换方差：主要用于评估图像的边缘锐利程度，低值表示图像较模糊。

'''
def calculate_blur_laplacian(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fm = cv2.Laplacian(gray, cv2.CV_64F).var()
    return fm

def fffff(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # 拉普拉斯变换
    gray_lap = cv2.Laplacian(gray, cv2.CV_64F)
    dst = cv2.convertScaleAbs(gray_lap)
    # 求取方差
    fm = dst.var()
    return fm


def calculate_entropy(image_path):
    """
    计算图像的熵。

    :param image: 输入的图像
    :return: 图像的熵
    """
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
    hist /= hist.sum()  # 归一化直方图
    entropy = -np.sum([p * np.log2(p) for p in hist if p != 0])
    return entropy


'''
2. 计算对比度
对比度是影响图像视觉效果的重要因素之一。较高的对比度通常意味着更好的视觉效果和更高的清晰度。
'''
def calculate_contrast(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    contrast = np.std(gray)
    return contrast

'''
4. 图像噪声水平
噪声也是影响图像质量的一个重要因素。可以通过分析图像中的噪声水平来评估其质量。
'''
def estimate_noise(image_path):
    image = cv2.imread(image_path, 0) # 以灰度模式读取
    noise = np.mean(np.abs(cv2.Laplacian(image, cv2.CV_64F)))
    return noise



def calculate_blur(image_path):
    # 读取图像
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("Image not found")

    # 计算梯度幅值
    grad_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
    gradient_magnitude = cv2.magnitude(grad_x, grad_y)

    # 计算梯度分布的标准差，标准差越大，表示边缘越不明显，即越模糊
    blur_measure = np.std(gradient_magnitude)
    return blur_measure

def calculate_contrast(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    contrast = np.std(gray)
    return contrast


def calculate_average_brightness(image_path):
    """
    计算图像的平均亮度。

    :param image: 输入的图像（BGR格式）
    :return: 平均亮度值
    """
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    avg_brightness = np.mean(gray)
    return avg_brightness



if __name__ == '__main__':
    path = "mix20241223_1.jpg"
    path = "000000.jpg"
    path = "0.jpg"

    data_dir = "./img"
    data_dir = "/home/ytusdc/Pictures/2"

    suffix = ['.jpg', '.png', '.jpeg', '.bmp']
    file_path_ls = [os.path.join(data_dir, x) for x in os.listdir(data_dir) if os.path.splitext(x.lower())[-1] in suffix]

    for path in sorted(file_path_ls):
        name = Path(path).name

        value = calculate_contrast(path)
        print(f"{name} : {value:.2f}")







from piq import brisque
import torch
from PIL import Image
import torchvision.transforms as transforms


def evaluate_image_quality_dl(image_path):
    """
    使用深度学习模型评估图像质量。

    :param image_path: 图像文件路径
    """
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize((384, 384))  # 调整大小以适应模型输入要求
    ])

    image = Image.open(image_path).convert('RGB')
    image_tensor = transform(image).unsqueeze(0)  # 添加批次维度

    score = brisque(image_tensor, data_range=1.1, reduction='none')
    print(f"图像的质量得分 (BRISQUE): {score.item()}")





import torch
from torchvision.transforms import ToTensor, Resize
from PIL import Image
import piq


def evaluate_exposure_dl(image_path):
    """
    使用预训练的深度学习模型评估图像的曝光度。

    :param image_path: 图像文件路径
    """
    transform = ToTensor()
    resize = Resize((256, 256))  # 调整大小以适应模型输入要求

    image = Image.open(image_path).convert('RGB')
    image_tensor = resize(transform(image)).unsqueeze(0)  # 添加批次维度

    # 使用PIQ库中的PSNR和SSIM作为示例
    psnr_value = piq.psnr(image_tensor, image_tensor, data_range=1.)
    ssim_value = piq.ssim(image_tensor, image_tensor, data_range=1.)

    print(f"图像的PSNR值: {psnr_value.item()}")
    print(f"图像的SSIM值: {ssim_value.item()}")




# 使用示例
image_path = '2.jpg'
evaluate_image_quality_dl(image_path)
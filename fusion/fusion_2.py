import time
import cv2
import numpy as np
from functools import wraps

def timing_decorator(func):
    @wraps(func) # @wraps接受一个函数来进行装饰，并加入了复制函数名称、注释文档、参数列表等等的功能
    def wrapper(*args, **kwargs):
        start_time = time.time()  # 记录开始时间
        result = func(*args, **kwargs)  # 调用被装饰的函数
        end_time = time.time()  # 记录结束时间
        print(f"Function {func.__name__} took {end_time - start_time:.4f} seconds to complete.")
        return result
    return wrapper

class Stitcher:
    # 拼接函数
    def stitch(self, images, ratio=0.75, reprojThresh=4.0, showMatches=False):
        """
        unpack the images, then detect keypoints and extract
        local invariant descriptors from them
        """
        # 获取输入图片
        (imageB, imageA) = images
        # 检测A、B图片的SIFT关键特征点，并计算特征描述子
        (kpsA, featuresA) = self.detectAndDescribe(imageA)
        (kpsB, featuresB) = self.detectAndDescribe(imageB)

        # 匹配两张图片的所有特征点，返回匹配结果
        M = self.matchKeypoints(kpsA, kpsB, featuresA, featuresB, ratio, reprojThresh)

        # 如果返回结果为空，没有匹配成功足够的特征点来进行全景拼接，退出算法
        if M is None:
            return None

        # 否则，提取匹配结果
        # H是3x3视角变换矩阵
        (matches, H, status) = M
        result_width = imageA.shape[1] + imageB.shape[1]
        result_height = imageA.shape[0]
        # 将图片A进行视角变换，warp_imgA 是变换后图片
        warp_imgA = cv2.warpPerspective(imageA, H, (result_width, result_height))

        cv2.imwrite("warp_imgA.jpg", warp_imgA)

        result = self.fusion(warp_imgA, imageB, result_width, result_height)

        # 检测是否需要显示图片匹配
        if showMatches:
            # 生成匹配图片
            vis = self.drawMatches(imageA, imageB, kpsA, kpsB, matches, status)
            # 返回结果
            return (result, vis)

        # 返回匹配结果
        return result, None

    def fusion(self, imgA_warp, imgB, width, height):

        # result_np = np.zeros((height, width, 3)).astype(int)
        result_np = imgA_warp.copy()
        # 融合
        for r in range(imgA_warp.shape[0]):
            left = 0
            for c in range(imgA_warp.shape[1] // 2):
                if imgA_warp[r, c].any():  # overlap
                    if left == 0:
                        left = c
                    alpha = (c - left) / (imgA_warp.shape[1] // 2 - left)
                    result_np[r, c] = imgB[r, c] * (1 - alpha) + imgA_warp[r, c] * alpha
                else:
                    result_np[r, c] = imgB[r, c]
        # cv2.imwrite("../temp_code/result_np.jpg", result_np)

        # 融合, result是图片A进行视角变换后图片
        # for r in range(result.shape[0]):
        #     left = 0
        #     for c in range(result.shape[1] // 2):
        #         if result[r, c].any():  # overlap
        #             if left == 0:
        #                 left = c
        #             alpha = (c - left) / (result.shape[1] // 2 - left)
        #             result[r, c] = imageB[r, c] * (1 - alpha) + result[r, c] * alpha
        #         else:
        #             result[r, c] = imageB[r, c]

        return result_np

    @timing_decorator
    def detectAndDescribe(self, image):
        # 将彩色图片转换成灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 建立SIFT生成器
        descriptor = cv2.SIFT_create()
        # 检测SIFT特征点，并计算描述子
        (kps, features) = descriptor.detectAndCompute(gray, None)
        # 将结果转换成NumPy数组
        kps = np.float32([kp.pt for kp in kps])
        # 返回特征点集，及对应的描述特征
        return kps, features

    def matchKeypoints(self, kpsA, kpsB, featuresA, featuresB, ratio, reprojThresh):
        # 建立暴力匹配器
        matcher = cv2.DescriptorMatcher_create("BruteForce")
        # 使用KNN检测来自A、B图的SIFT特征匹配对，K=2
        rawMatches = matcher.knnMatch(featuresA, featuresB, 2)

        matches = []
        for m in rawMatches:
            # 当最近距离跟次近距离的比值小于ratio值时，保留此匹配对
            if len(m) == 2 and m[0].distance < m[1].distance * ratio:
                # 存储两个点在featuresA, featuresB中的索引值
                matches.append((m[0].trainIdx, m[0].queryIdx))

        # 当筛选后的匹配对大于4时，计算视角变换矩阵
        if len(matches) > 4:
            # 获取匹配对的点坐标
            ptsA = np.float32([kpsA[i] for (_, i) in matches])
            ptsB = np.float32([kpsB[i] for (i, _) in matches])
            # 计算视角变换矩阵
            (H, status) = cv2.findHomography(ptsA, ptsB, cv2.RANSAC, reprojThresh)
            print(H)
            # 返回结果
            return (matches, H, status)
        # 如果匹配对小于4时，返回None
        return None

    def drawMatches(self, imageA, imageB, kpsA, kpsB, matches, status):
        # 初始化可视化图片，将A、B图左右连接到一起
        (hA, wA) = imageA.shape[:2]
        (hB, wB) = imageB.shape[:2]
        vis = np.zeros((max(hA, hB), wA + wB, 3), dtype="uint8")
        vis[0:hA, 0:wA] = imageA
        vis[0:hB, wA:] = imageB

        # 联合遍历，画出匹配对
        for ((trainIdx, queryIdx), s) in zip(matches, status):
            # 当点对匹配成功时，画到可视化图上
            if s == 1:
                # 画出匹配对
                ptA = (int(kpsA[queryIdx][0]), int(kpsA[queryIdx][1]))
                ptB = (int(kpsB[trainIdx][0]) + wA, int(kpsB[trainIdx][1]))
                cv2.line(vis, ptA, ptB, (0, 255, 0), 1)

        # 返回可视化结果
        return vis


if __name__ == '__main__':
    start_time = time.time()
    # 读取拼接图片

    # imageA = cv2.imread("/home/ytusdc/fusion_test/1/11.jpg")
    imageA = cv2.imread("/home/ytusdc/fusion_test/1/14.jpg")
    imageB = cv2.imread("/home/ytusdc/fusion_test/1/15.jpg")


    # imageA = cv2.imread("./1112.jpg")
    # imageB = cv2.imread("/home/ytusdc/fusion_test/1/resize_10.jpg")


    # 把图片拼接成全景图
    stitcher = Stitcher()
    (result, vis) = stitcher.stitch([imageA, imageB], showMatches=True)
    if vis is not None:
        cv2.imwrite("img1.jpg", vis)
    cv2.imwrite("img2.jpg", result)
    end_time = time.time()
    print("共耗时" + str(end_time - start_time))
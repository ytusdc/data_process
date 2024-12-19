import cv2
import numpy as np



def main():
    p1 = "/home/ytusdc/fusion_test/1/14.jpg"
    p2 = "/home/ytusdc/fusion_test/1/15.jpg"
    p3 = "/home/ytusdc/fusion_test/1/16.jpg"
    p4 = "/home/ytusdc/fusion_test/1/17.jpg"
    p5 = "/home/ytusdc/fusion_test/1/18.jpg"

    img1 = cv2.imread(p1)
    img2 = cv2.imread(p2)
    img3 = cv2.imread(p3)
    img4 = cv2.imread(p4)
    img5 = cv2.imread(p5)

    h1,w1,_=img1.shape
    h2,w2,_=img2.shape
    h3,w3,_=img3.shape
    h4,w4,_=img4.shape
    h5,w5,_=img5.shape

    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    gray3 = cv2.cvtColor(img3, cv2.COLOR_BGR2GRAY)
    gray4 = cv2.cvtColor(img4, cv2.COLOR_BGR2GRAY)
    gray5 = cv2.cvtColor(img5, cv2.COLOR_BGR2GRAY)

    sift = cv2.SIFT_create()

    kp1, desc1 = sift.detectAndCompute(gray1, None)
    kp2, desc2 = sift.detectAndCompute(gray2, None)
    kp3, desc3 = sift.detectAndCompute(gray3, None)
    kp4, desc4 = sift.detectAndCompute(gray4, None)
    kp5, desc5 = sift.detectAndCompute(gray5, None)

    bf = cv2.BFMatcher(crossCheck=False)

    # 1拼接到2
    matches12 = bf.knnMatch(desc1,desc2, k=2)
    good12 = []
    for m, n in matches12:
        if m.distance < 0.5 * n.distance:
            good12.append(m)

    good12 = sorted(good12, key=lambda x: x.distance)[:len(good12) // 2]
    pt12_src = np.float32([kp1[m.queryIdx].pt for m in good12]).reshape(-1, 1, 2)
    pt12_dst = np.float32([kp2[m.trainIdx].pt for m in good12]).reshape(-1, 1, 2)

    H12, mask12 = cv2.findHomography(pt12_src,pt12_dst,cv2.RANSAC,ransacReprojThreshold=4.0)
    w12 = w1 + w2
    h = max(h1, h2,h3,h4,h5)

    shft12 = np.array([[1.0, 0, w1], [0, 1.0, 0], [0, 0, 1.0]], np.float64)
    M12 = np.dot(shft12, H12)
    img12 = cv2.warpPerspective(img1, M12, (w12, h))
    cv2.imwrite("12.jpg", img12)
    img12[0:h2,-w2:] = img2
    cv2.imwrite("mix12.jpg", img12)

    #12拼接到3
    matches123 = bf.knnMatch(desc2,desc3, k=2)
    good123 = []
    for m, n in matches123:
        if m.distance < 0.5 * n.distance:
            good123.append(m)

    good123 = sorted(good123, key=lambda x: x.distance)[:len(good123) // 2]
    pt123_src = np.float32([kp2[m.queryIdx].pt for m in good123]).reshape(-1, 1, 2)
    pt123_dst = np.float32([kp3[m.trainIdx].pt for m in good123]).reshape(-1, 1, 2)

    pt123_src[:,0,0]+=w1
    H123,mask123 = cv2.findHomography(pt123_src,pt123_dst,cv2.RANSAC,ransacReprojThreshold=4.0)
    w123 = w1+w2+w3

    shft123 = np.array([[1.0, 0, w12], [0, 1.0, 0], [0, 0, 1.0]], np.float64)
    M123 = np.dot(shft123,H123)
    img123 = cv2.warpPerspective(img12,M123,(w123, h))
    cv2.imwrite("123.jpg", img123)

    img123[0:h3,-w3:] = img3
    cv2.imwrite("mix123.jpg",img123)

    # 5拼接到4
    matches54 = bf.knnMatch(desc5,desc4, k=2)
    good54 = []
    for m, n in matches54:
        if m.distance < 0.5 * n.distance:
            good54.append(m)

    good54 = sorted(good54, key=lambda x: x.distance)[:len(good54) // 2]
    pt54_src = np.float32([kp5[m.queryIdx].pt for m in good54]).reshape(-1, 1, 2)
    pt54_dst = np.float32([kp4[m.trainIdx].pt for m in good54]).reshape(-1, 1, 2)

    H54,mask54 = cv2.findHomography(pt54_src,pt54_dst,cv2.RANSAC,ransacReprojThreshold=4.0)
    w54 = w4 + w5

    img54 = cv2.warpPerspective(img5,H54,(w54,h))
    cv2.imwrite("54.jpg", img54)

    img54[:h4,:w4]=img4
    cv2.imwrite("mix54.jpg",img54)
    #54转换到3
    matches543 = bf.knnMatch(desc4, desc3, k=2)
    good543 = []
    for m, n in matches543:
        if m.distance < 0.5 * n.distance:
            good543.append(m)

    good543 = sorted(good543, key=lambda x: x.distance)[:len(good543) // 2]
    pt543_src = np.float32([kp4[m.queryIdx].pt for m in good543]).reshape(-1, 1, 2)
    pt543_dst = np.float32([kp3[m.trainIdx].pt for m in good543]).reshape(-1, 1, 2)

    H543, mask543 = cv2.findHomography(pt543_src, pt543_dst, cv2.RANSAC, ransacReprojThreshold=4.0)
    w543 = w4 + w5+w3

    img543 = cv2.warpPerspective(img54, H543, (w543, h))
    cv2.imwrite("543.jpg", img543)

    result2 = np.zeros((h,w1+w2+w3+w4+w5,3),np.uint8)
    result2[:,-w543:]=img543
    result2[:,:w123]=img123

    cv2.imwrite("mix145678.jpg", result2)


if __name__=="__main__":
    main()

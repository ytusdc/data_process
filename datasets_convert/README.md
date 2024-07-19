# 本项目用于coco、VOC、YOLO标签转换

<details open>
<summary>VOC</summary>

### VOC数据集由五个部分构成：JPEGImages，Annotations，ImageSets，SegmentationClass以及SegmentationObject.

- JPEGImages：存放的是训练与测试的所有图片。
- Annotations：里面存放的是每张图片打完标签所对应的XML文件。
- ImageSets：ImageSets文件夹下本次讨论的只有Main文件夹，此文件夹中存放的主要又有四个文本文件test.txt,train.txt,trainval.txt,val.txt, 其中分别存放的是测试集图片的文件名、训练集图片的文件名、训练验证集图片的文件名、验证集图片的文件名。
- SegmentationClass与SegmentationObject：存放的都是图片，且都是图像分割结果图，对目标检测任务来说没有用。class segmentation 标注出每一个像素的类别 
- object segmentation 标注出每一个像素属于哪一个物体。

### XML标注格式
```
<annotation>
  <folder>17</folder> # 图片所处文件夹
  <filename>77258.bmp</filename> # 图片名
  <path>~/frcnn-image/61/ADAS/image/frcnn-image/17/77258.bmp</path>
  <source>  #图片来源相关信息
    <database>Unknown</database>  
  </source>
  <size> #图片尺寸
    <width>640</width>
    <height>480</height>
    <depth>3</depth>
  </size>
  <segmented>0</segmented>  #是否有分割label
  <object> 包含的物体
    <name>car</name>  #物体类别
    <pose>Unspecified</pose>  #物体的姿态
    <truncated>0</truncated>  #物体是否被部分遮挡（>15%）
    <difficult>0</difficult>  #是否为难以辨识的物体， 主要指要结体背景才能判断出类别的物体。虽有标注， 但一般忽略这类物体
    <bndbox>  #物体的bound box
      <xmin>2</xmin>     #左
      <ymin>156</ymin>   #上
      <xmax>111</xmax>   #右
      <ymax>259</ymax>   #下
    </bndbox>
  </object>
</annotation>
```
</details>

<details open>
<summary>COCO</summary>

### COCO数据集现在有3种标注类型：
- object instances（目标实例） 
- object keypoints（目标上的关键点）
- image captions（看图说话）

这3种类型共享这些基本类型：info、image、license，使用JSON文件存储。

### json标注格式
以Object Instance为例，这种格式的文件从头至尾按照顺序分为以下段落：

info: 信息，有关数据集的元数据，例如版本、创建日期和贡献者信息
licenses: 许可证，与数据集中的图像关联的许可证
images: 图片，数据集中所有图像的列表，包含文件路径、高度、宽度和其他元数据等详细信息
annotations: 注释，每个图像的所有对象注释的列表，包含对象类别、边界框坐标和分割掩模（如果可用）
categories: 类别，所有数据集对象类别的列表，包含数据集中所有对象类别的名称和对应ID

```
{
    "info": info,               # dict 
    "licenses": [license],      # list,内部是dict
    "images": [image],          # list,内部是dict
    "annotations": [annotation],# list,内部是dict
    "categories": [category]    # list,内部是dict
}

下面是对上面各个字段内容的详细解释
————————————————————————————————————————————————————————————

info{                           # 数据集信息描述
    "year": int,                # 数据集年份
    "version": str,             # 数据集版本
    "description": str,         # 数据集描述
    "contributor": str,         # 数据集提供者
    "url": str,                 # 数据集下载链接
    "date_created": datetime,   # 数据集创建日期
}
license{
    "id": int,
    "name": str,
    "url": str,
} 
image{      # images是一个list,存放所有图片(dict)信息。image是一个dict,存放单张图片信息 
    "id": int,                  # 图片的ID编号（每张图片ID唯一）
    "width": int,               # 图片宽
    "height": int,              # 图片高
    "file_name": str,           # 图片名字，图像的文件名
    "license": int,             # 协议，图片的许可id
    "flickr_url": str,          # flickr链接地址
    "coco_url": str,            # 网络连接地址（如果有）
    "date_captured": datetime,  # 数据集获取日期（如果有）
}
annotation{     # annotations是一个list,存放所有标注(dict)信息。annotation是一个dict,存放单个目标标注信息。
    "id": int,                  # 目标对象ID（每个对象ID唯一），每张图片可能有多个目标
    "image_id": int,            # 对应图片ID
    "category_id": int,         # 对应类别ID，与categories中的ID对应
    "segmentation": RLE or [polygon],   # 实例分割，对象的边界点坐标[x1,y1,x2,y2,....,xn,yn]
    "area": float,              # 对象区域面积
    "bbox": [xmin,ymin,width,height], # 目标检测，对象定位边框[x,y,w,h]，左上角的 x 和 y 坐标以及框的宽度和高度
    "iscrowd": 0 or 1,          # 表示是否是人群
}
categories{                     # 类别描述
    "id": int,                  # 类别对应的ID（0默认为背景），类别的唯一整数标识符
    "name": str,                # 类别名字
    "supercategory": str,       # 主类别名字，可选字段，指定比当前类别name更广泛的类别
}
```

</details>

<details open>
<summary>YOLO</summary>

### YOLO格式数据集
- images:存放图片数据
- labels:存放标注txt文本
- 一个标注信息txt对应一张图片，如xxx.txt对应xxx.jpg所有的标注信息
- yolo 

### YOLO标注格式：txt格式
```
<object-class> <x> <y> <width> <height>
```
for example

```
0 0.412500 0.318981 0.358333 0.636111
```

- object-class：对象的标签索引，
  > yolo 标注的类别只有索引，这是由于yolo训练时候都会有一个 yaml 文件，yaml中存放了类别标签，训练时候会自动解析，通过标签id查找到标签名，yaml格式 参考yaml文件夹下的文件，
  > 其中 [names] 标签下存放的是 yolo 标签id和对应的类别
  
- x,y是目标的中心坐标，width,height是目标的宽和高。这些坐标是通过归一化的，其中x，width是使用原图的width进行归一化；而y，height是使用原图的height进行归一化。
- 如果其他数据集转换成yolo时候不传入yaml标签文件，程序会对标签自动排序，并生成一个对应的yaml文件， 这一点需要格外注意

- COCO、YOLO、VOC、json数据格式转换脚本 https://zhuanlan.zhihu.com/p/653184708
- 目标检测coco voc yolo格式转换和划分数据集 https://blog.csdn.net/weixin_56314292/article/details/131562730
- YOLO系列之数据划分和数据格式转换篇 https://download.csdn.net/blog/column/12475400/135069518

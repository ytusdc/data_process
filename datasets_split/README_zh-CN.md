coco_split.py  
该文件划分的是 json文件，将一个json文件划分为 用作 train/test/val的数据集 

通常，自定义图片都是一个大文件夹，里面全部都是图片， 需要我们自己去对图片进行训练集、验证集、测试集的划分，
如果数据量比较少，可以不划分验证集。下面是划分脚本的具体用法：

> python coco_split.py --json {COCO label json 路径} \
                                --out-dir {划分 label json 保存根路径} \
                                --ratios {划分比例} \
                                [--shuffle] \
                                [--seed {划分的随机种子}]

--json 总的json文件  
--out-dir 划分后的json文件存放路径  
--ratios：划分的比例，如果只设置了 2 个，则划分为 trainval + test； 如果设置为 3 个，则划分为 train + val + test。支持两种格式 —— 整数、小数：
整数：按比例进行划分，代码中会进行归一化之后划分数据集。例子： --ratio 2 1 1（代码里面会转换成 0.5 0.25 0.25） or --ratio 3 1（代码里面会转换成 0.75 0.25）
小数：划分为比例。如果加起来不为 1 ，则脚本会进行自动归一化修正。例子： --ratio 0.8 0.1 0.1 or --ratio 0.8 0.2  
--shuffle: 是否打乱数据集再进行划分。  
--seed：设定划分的随机种子，不设置的话自动生成随机种子。

> python tools/misc/coco_split.py --json ./data/cat/annotations/annotations_all.json \
                                --out-dir ./data/cat/annotations \
                                --ratios 0.8 0.2 \
                                --shuffle \
                                --seed 10
 

split_data.py 适用于
'''
适用于数据结构为
.
├── images
│   ├── beida_20220321_29.jpg
│   └── beida_20220321_6.jpg
└── labels
    ├── beida_20220321_29.txt
    └── beida_20220321_6.txt
'''
import os
import json
from xml.etree import ElementTree as ET
from collections import defaultdict
from datetime import datetime
from tqdm import tqdm

class VocToCoco:
    def __init__(self, voc_ann_dir: str, output_coco_path: str) -> None:
        self.voc_ann_dir = voc_ann_dir
        self.output_coco_path = output_coco_path
        self.categories_count = 1
        self.images = []
        self.categories = {}
        self.annotations = []
        # self.data = defaultdict(list)

    # 图片处理
    def images_handle(self, root: ET.Element, img_id: int) -> None:
        filename = root.find('filename').text.strip()
        width = int(root.find('size').find('width').text)
        height = int(root.find('size').find('height').text)

        image_item = {
            'id': int(img_id),
            'file_name': filename,
            'height': height,
            'width': width,
            # 'license' : None,
            # 'flickr_url' : None,
            # 'coco_url' : None,
            # 'date_captured' : str(datetime.today())
        }
        self.images.append(image_item)

    # 标签转换
    def categories_handle(self, category: str) -> None:
        if category not in self.categories:
            self.categories[category] = {'id': len(self.categories) + 1, 'name': category}

    # 标注转换
    def annotations_handle(self, bbox: ET.Element, img_id: int, category: str) -> None:
        x1 = int(bbox.find('xmin').text)
        y1 = int(bbox.find('ymin').text)
        x2 = int(bbox.find('xmax').text)
        y2 = int(bbox.find('ymax').text)

        annotation_item ={
            'id': self.categories_count,
            'image_id': int(img_id),
            'category_id': self.categories[category].get('id'),
            'bbox': [x1, y1, x2 - x1, y2 - y1],    # x, y, w, h
            'iscrowd': 0,
            'ignore' : 0
        }
        self.annotations.append(annotation_item)
        self.categories_count += 1

    def parse_voc_annotation(self) -> None:
        for img_id, filename in tqdm(enumerate(os.listdir(self.voc_ann_dir), 1)):
            xml_file = os.path.join(self.voc_ann_dir, filename)
            tree = ET.parse(xml_file)
            root = tree.getroot()

            self.images_handle(root, img_id)

            for obj in root.iter('object'):
                category = obj.find('name').text
                self.categories_handle(category)

                bbox = obj.find('bndbox')
                self.annotations_handle(bbox, img_id, category)

        # 构建 coco 字典
        coco_data = dict()
        coco_data['images'] = self.images
        coco_data['annotations'] = self.annotations
        coco_data['categories'] = list(self.categories.values())

        # self.data['images'] = self.images
        # self.data['categories'] = list(self.categories.values())
        # self.data['annotations'] = self.annotations

        parent_dir = os.path.dirname(output_coco_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        with open(self.output_coco_path, 'w') as f_w:
            json.dump(coco_data, f_w)


if __name__ == "__main__":
    # Example usage
    voc_label_dir = './data/labels/voc'
    img_dir = './data/images'
    output_coco_path = './result/convert/coco/train.json'

    voc2coco = VocToCoco(voc_label_dir, output_coco_path)
    voc2coco.parse_voc_annotation()


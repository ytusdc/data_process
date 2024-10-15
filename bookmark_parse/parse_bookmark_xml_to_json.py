# -*- coding: utf-8 -*-
import os
import json
import xmltodict

"""
xml格式书签 转换为 json
"""
def xml_to_JSON(xml_file):
    # 格式转换
    try:
        with open(xml_file, encoding='utf-8') as f:
            xml_data = f.read()
            convertJson = xmltodict.parse(xml_data, encoding='utf-8')
            jsonStr = json.dumps(convertJson, indent=1, ensure_ascii=False)
            return jsonStr
    except Exception:
        print('something has occurred')

def write_json(json_data, save_file):
    with open(save_file, 'w+', encoding='utf-8') as f:
        f.write(json_data)

if __name__ == '__main__':
    html_file = "./bookmarks.xml"
    json_data = xml_to_JSON(html_file)
    pass

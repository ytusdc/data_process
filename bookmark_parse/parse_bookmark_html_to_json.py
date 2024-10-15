# -*- coding: utf-8 -*-
# author:           inspurer(月小水长)
# create_time:      2021/12/28 22:18
# 运行环境            Python3.6+
# github            https://github.com/inspurer
# github            https://github.com/inspurer/ChromeBookmarkVisual/tree/master
# 微信公众号          月小水长

from lxml import etree
import json

"""
html 格式书签 转换为 json
"""

def get_regular_html(bookmark_html_file):
    """
    在 lxml 解析过程中发现，由于导出的 html 中许多 DT、H3 标签没有闭合，导致解析紊乱，
    故先将 html 内容规范化处理之。
    """
    with open(bookmark_html_file, mode='r', encoding='utf-8-sig') as fp:
        html_content = fp.read()
    '''
     先规则 html 标签，否则 etree.HTML 解析的结构很混乱
    '''
    html_content = html_content.replace(r'<p>', '')
    html_content = html_content.replace(r'</H3>', r'</H3></DT>')
    html_content = html_content.replace(r'</A>', r'</A></DT>')
    return html_content

'''
name_key, children_key, url_key 三个变量在 parse_html_recursive， html_2_json 函数中都会用到
因此这里定义成全局变量
'''
name_key, children_key, url_key = 'name', 'children', 'url'

def parse_html_recursive(root_html):
    """
    使用递归法解析 lxml 成 json
    """
    children = []
    children_html = root_html.xpath('./child::*')
    for index, ele in enumerate(children_html):
        tag_name = ele.tag.strip()
        if tag_name == 'dt':
            if ele.xpath('./h3'):
                name = ele.xpath('./h3/text()')[0].strip()
                # if name in exclude_collection:  # 不包含的name，暂时用不到
                #     continue
                children.append({
                    name_key: name,
                    children_key: parse_html_recursive(children_html[index + 1])
                })
            elif ele.xpath('./a'):
                if len(ele.xpath('./a/text()')) == 0:
                    print('过滤掉没有书签名的')
                    continue
                url = ele.xpath('./a/@href')[0]
                name = ele.xpath('./a/text()')[0].strip()
                children.append({
                    name_key: name,
                    url_key: url
                })
    return children

def html_2_json(bookmark_html_file, root_name=None):
    """
    html 文件转 json 格式
    Args:
        bookmark_html_file:
        root_name: 根节点名，可以自己定义，如果None 则会默认设置为 '书签'
    Returns:
    """
    html = etree.HTML(get_regular_html(bookmark_html_file))

    """
    通过原始html统计标签个数
    """
    # links = html.xpath('//dt/a')
    # print(f"html 中得到的书签数量是：{len(links)}")
    if root_name is None:
        root_name = '书签'
    bookmark_map_json = {
        name_key: root_name,
    }
    root = html.xpath('//dl[1]/dl[1]')[0]
    bookmark_map_json[children_key] = parse_html_recursive(root)
    return bookmark_map_json

def writejson(json_data, save_json_file):
    with open(save_json_file, 'w', encoding='utf-8-sig') as f:
        f.write(json.dumps(json_data, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    html_file = "/home/ytusdc/Documents/favorites_9_25_24_111.html"
    json_data = html_2_json(html_file)
    pass






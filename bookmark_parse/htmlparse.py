from bs4 import BeautifulSoup
import os
bookmarks_file = '/home/ytusdc/Documents/favorites_9_30_24.html'  # 替换为你的书签文件路径
# bookmarks_file = '/home/ytusdc/Documents/test.html'  # 替换为你的书签文件路径
from bs4 import BeautifulSoup


from bs4 import BeautifulSoup

class BookmarkNode:
    def __init__(self, name, url=None, tags=None):
        self.name = name
        self.url = url
        self.tags = tags
        self.children = []

    def add_child(self, node):
        self.children.append(node)

    def __repr__(self):
        return f"{self.name} ({self.url})" if self.url else self.name

def parse_bookmark_html(file_path):
    # 读取HTML书签文件
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # 创建根节点
    root_node = BookmarkNode("Root")

    # 解析书签和文件夹
    def parse_node(parent, dl):
        for dt in dl.find_all('dt'):
            if dt.h3:
                # 文件夹
                folder_name = dt.h3.text.strip()
                folder_node = BookmarkNode(folder_name)
                parent.add_child(folder_node)
                if dl := dt.find_next_sibling('dl'):
                    parse_node(folder_node, dl)
            elif dt.a:
                # 书签
                link_name = dt.a.text.strip()
                link_url = dt.a.get('href')
                link_tags = dt.a.get('tags', '').split(',')
                link_node = BookmarkNode(link_name, link_url, link_tags)
                parent.add_child(link_node)

    # 开始解析
    if main_dl := soup.find('dl'):
        parse_node(root_node, main_dl)

    return root_node

def print_bookmark_tree(node, level=0):
    indent = "  " * level
    print(f"{indent}{node}")
    for child in node.children:
        print_bookmark_tree(child, level + 1)

# 使用函数
bookmarks_file = bookmarks_file # 替换为你的书签文件路径
root_node = parse_bookmark_html(bookmarks_file)

print("Bookmarks Tree:")
print_bookmark_tree(root_node)





# def parse_html_with_hierarchy(file_path):
#     # 读取HTML文件
#     with open(file_path, 'r', encoding='utf-8') as file:
#         soup = BeautifulSoup(file, 'html.parser')
#
#     # 从HTML中获取主<dl>元素
#     main_dl = soup.find('dl')
#
#     # 递归解析函数
#     def parse_element(parent, element):
#
#         name = element.name
#
#         if element.name == 'dt':
#             # sub_element = element.find_next_sibling('dl')
#             sub_element = element.next_sibling
#             while sub_element and sub_element.name != 'dl':
#                 sub_element = sub_element.next_sibling
#
#             if sub_element:
#                 # 如果有子元素，则创建新的子树
#                 parse_element(parent, sub_element)
#             else:
#                 # 否则是书签
#                 anchor = element.find('a')
#                 if anchor:
#                     bookmark = {
#                         'title': anchor.text.strip(),
#                         'url': anchor.get('href'),
#                     }
#                     parent.append(bookmark)
#         elif element.name == 'dl':
#             # 新建一个子列表来存储子元素
#             children = []
#             parent.append(children)
#             for child in element.find_all('dt'):
#                 parse_element(children, child)
#
#     # 初始化根节点
#     root = []
#     parse_element(root, main_dl)
#
#     return root
#
# # 使用函数
# html_file = bookmarks_file
# tree_structure = parse_html_with_hierarchy(html_file)
#
# # 输出结果
# def print_structure(structure, indent=0):
#     prefix = "  " * indent
#     for item in structure:
#         if isinstance(item, list):
#             print(f"{prefix}- Folder:")
#             print_structure(item, indent + 1)
#         else:
#             print(f"{prefix}- Bookmark: {item['title']} ({item['url']})")
#
# print_structure(tree_structure)
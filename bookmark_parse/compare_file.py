from pathlib import Path
import pathlib
import difflib
import shutil
import os

import fitz   # pdf 操作

def get_dict(root_dir):
    file_ls = [str(f) for f in Path(root_dir).rglob(f"*.*") if Path(f).is_file()]
    file_dict = {}
    existname_set = set()
    pdf_extensions = ['.pdf']
    pdf_extensions = ['.pdf', '.rar', '.zip']
    for path in file_ls:
        file_name, file_extension = os.path.splitext(path)
        if file_extension.lower() not in pdf_extensions:
            continue
        name = path.split("\\")[-1]
        if name in existname_set:
            print(f"have same name file {name}")
            continue
        file_dict[name] = path
        existname_set.add(name)
    return file_dict

def find_str_inPdf(root_dir, find_str):
    file_ls = [str(f) for f in Path(root_dir).rglob(f"*.*") if Path(f).is_file()]
    count_find = 0
    for file in file_ls:
        # 打开 PDF 文件
        pdf_document = fitz.open(file)

        for page in pdf_document:
            text = page.get_text("text")
            if find_str in text:
                name = file.split("\\")[-1]
                count_find += 1
                print(name)
                # break
    print(f"找到的/总数：{count_find}/{len(file_ls)}")

def find_text(input_file):
    targettext_list = ["1101284955", "老庄日记", "qiyi6999"]
    with fitz.open(input_file) as doc:
        total_pages = doc.page_count
        for page_num in range(total_pages):
            page = doc.load_page(page_num)
            text = page.get_text()
            for target in targettext_list:
                if target in text:
                    return True, target, page_num


        # for page in doc.pages():
        #     text = page.get_text()
        #     for target in targettext_list:
        #         if target in text:
        #             return True, target
    return False, "", ""

def find_image(input_file):
    with fitz.open(input_file) as doc:
        for page in doc.pages():
            images_ls = page.get_images()
            if len(images_ls) > 0:
                return True
    return False

'''
search_text 是否查找文字
search_image 是否查找图片
mark_savedir 有水印的文件移动的savedir
'''
def find_watermark(root_dir, search_text=True, search_image=False, mark_savedir=None):
    file_dict = get_dict(root_dir)
    count_text = 0
    count_image = 0
    if search_text:
        for _, path in file_dict.items():
            result, target, page_num = find_text(path)
            if result:
                print(f"{path}，{page_num}页， 找到文字信息: {target}")
                count_text += 1
                if mark_savedir is not None:
                    shutil.move(path, mark_savedir)

    if search_image:
        for _, path in file_dict.items():
            if find_image(path):
                print(f"{path}，找到图片信息")
                count_image += 1
    print(f"找到文字的 {count_text} 个， 找到图片的 {count_image} 个")


def move2Folder(base_dir, serarch_dir, save_dir, threshold=0.6):
    dict_base = get_dict(base_dir)
    dict_search = get_dict(serarch_dir)

    for ori_file_name in dict_base.keys():
        for des_file_name in dict_search.keys():
            if difflib.SequenceMatcher(None, ori_file_name, des_file_name).quick_ratio() > threshold:
                file_path = dict_search[des_file_name]
                shutil.move(file_path, save_dir)

def rename_file(root_dir, begin=1):

    # file_ls = [str(f) for f in Path(root_dir).rglob(f"*.*") if Path(f).is_file()]
    file_ls = os.listdir(root_dir)
    existname_set = set()
    pdf_extensions = ['.pdf', '.doc']
    new_name_ls = []

    new_old_name_dict = {}

    for path in file_ls:
        file_name, file_extension = os.path.splitext(path)
        if file_extension.lower() not in pdf_extensions:
            continue
        old_name = Path(path).name
        split_ls = old_name.split("-")
        if len(split_ls) > 1:
            new_name = "-".join(split_ls[1:])
        else:
            new_name = "-".join(split_ls[:])
        new_name_ls.append(new_name)
        new_old_name_dict[new_name] = old_name
        ceshi = sorted(new_name_ls)

    for newname in sorted(new_name_ls):
        old = new_old_name_dict[newname]

        new = str(begin) + "-" + newname
        begin += 1

        shutil.move(Path(root_dir, old), Path(root_dir, new))

        print(f"{old}")
        print(f"{new}")


'''
# 查找 重名文件，并且比较文件大小
samesize_dir: 被查找到的与基准文件相同类似的文件移动到samesize_dir
ismove
threshold 文件名相似度阈值
ismovesamesize = false  移动相同大小尺寸的文件
ismovesimlarname = false  移动相似度为threshold的文件
'''
def find_duplicate_files(ori_dir, des_dir, samesize_dir, threshold=0.7, ismovesamesize=False, ismovesimlarname=False):
    dict_ori = get_dict(ori_dir)
    dict_des = get_dict(des_dir)

    if not Path(samesize_dir).exists():
        Path(samesize_dir).mkdir()

    count_simlar = 0
    count_equal = 0
    for ori_file_name in dict_ori.keys():
        for des_file_name in dict_des.keys():
            if difflib.SequenceMatcher(None, ori_file_name, des_file_name).quick_ratio() > threshold:
                movefile_path = dict_des[des_file_name]
                if not Path(movefile_path).exists():
                    continue
                size_ori = Path(dict_ori[ori_file_name]).stat().st_size
                size_des = Path(movefile_path).stat().st_size
                parentname_ori = Path(dict_ori[ori_file_name]).parent.name
                parentname_des = Path(dict_des[des_file_name]).parent.name

                if size_ori == size_des:
                    count_equal += 1
                    if ismovesamesize:
                        print("************Same****************")
                        print(f"{parentname_ori}/{ori_file_name}, {size_ori}")
                        print(f"{parentname_des}/{des_file_name}, {size_des}")
                        print("#############################")
                        shutil.move(movefile_path, samesize_dir)
                else:
                    count_simlar += 1
                    if ismovesimlarname:
                        print("*************Simlar***************")
                        print(f"{parentname_ori}/{ori_file_name}, {size_ori}")
                        print(f"{parentname_des}/{des_file_name}, {size_des}")
                        print("#############################")
                        # shutil.move(movefile_path, samesize_dir)
                # dict_ori.pop(ori_file_name)
                # dict_des.pop(des_file_name)
    print(f"文件名相似度>{threshold},的文件个数：{count_simlar}")
    print(f"文件名相似度>{threshold},同时size大小相同的文件个数：{count_equal}")
    print(f"基准文件个数/被比较文件个数：{len(dict_ori)}/{len(dict_des)}")



def fun_1():
    # 需要被比较，作为基准的文件夹
    # dir_ori = r"F:\天涯神帖_20240108"
    dir_ori = r"F:\天涯神帖_20240315整理"
    # dir_ori = r"F:\天涯神帖_20240315整理\2-【人在江湖】【古今热点】【成长箴言】【煮酒论史】"
    # dir_ori = r"F:\天涯神帖_20240315整理\1-【莲蓬鬼话】【玄幻灵异】【中医命理】"
    # 被比较与 ori 异同的文件夹

    dir_des = r"F:\迅雷下载\天涯合集全"
    # dir_des = r"E:\BaiduNetdiskDownload\0313\神贴补充中"
    # dir_des 中与dir_ori文件size相同的，转移到 dir_samesiz， 方便处理dir_des剩余的文件
    dir_samesiz = r"F:/same"


    threshold_value = 0.7
    movesamesize = True
    movesimlarname = True
    find_duplicate_files(dir_ori, dir_des, dir_samesiz, threshold=threshold_value, ismovesamesize=movesamesize, ismovesimlarname=movesimlarname)



def fun_2():
    dir_search = r"F:\天涯神帖_20240108"
    dir_search = r"F:\天涯神帖_20240315整理"
    issearchtext = True
    issearchimage = False
    mark_movedir = None
    # mark_movedir = r"E:/same"
    find_watermark(dir_search, search_text=issearchtext, search_image=issearchimage, mark_savedir=mark_movedir)


def fun_3():
    root = r"F:\天涯神帖_20240315整理\4-【故事小说】"
    rename_file(root)

if __name__ == '__main__':

    fun_1()
    # fun_2()
    # fun_3()













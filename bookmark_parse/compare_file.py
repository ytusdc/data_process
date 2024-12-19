from pathlib import Path
import difflib
import shutil
import os
import fitz

# 这个函数暂时没用到
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
 pip install fitz -i https://pypi.tuna.tsinghua.edu.cn/simple
 pip install pymupdf -i https://pypi.tuna.tsinghua.edu.cn/simple
'''
class Pdf_Class:
    def __init__(self):
        pass

    def find_str_inPdf(self, root_dir, find_str):
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

    def find_text(self, input_file):
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

    def find_image(self, input_file):
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
    def find_watermark(self, root_dir, search_text=True, search_image=False, mark_savedir=None):
        file_dict = get_name_path_dict(root_dir)
        count_text = 0
        count_image = 0
        if search_text:
            for _, path in file_dict.items():
                result, target, page_num = self.find_text(path)
                if result:
                    print(f"{path}，{page_num}页， 找到文字信息: {target}")
                    count_text += 1
                    if mark_savedir is not None:
                        shutil.move(path, mark_savedir)

        if search_image:
            for _, path in file_dict.items():
                if self.find_image(path):
                    print(f"{path}，找到图片信息")
                    count_image += 1
        print(f"找到文字的 {count_text} 个， 找到图片的 {count_image} 个")


def get_name_path_dict(root_dir, extensions=None):
    # 查找当前目录及其子目录下的所有文件夹
    file_ls = [str(f) for f in Path(root_dir).rglob(f"*.*") if Path(f).is_file()]
    name_path_dict = {}
    exist_name_set = set()
    # 需要查找的文件类型后缀
    if extensions is None:
        extensions = ['.pdf', '.rar', '.zip', '.doc', '.docx']

    for path in file_ls:
        # _, file_extension = os.path.splitext(path)
        file_extension = Path(path).suffix
        if file_extension.lower() not in extensions:
            continue
        name = Path(path).name
        if name in exist_name_set:
            print(f"have same name file: {name}")
            continue
        name_path_dict[name] = path
        exist_name_set.add(name)
    return name_path_dict


class Duplicate:
    def __init__(self, ori_dir, des_dir, move_dir,
                 ismovesamesize=False,
                 ismovesimlarname=False,
                 threshold=0.7):
        """
        Args:
            ori_dir:  原始文件路径,  # 需要被比较，作为基准的文件夹
            des_dir:  可能有重复文件的路径,   # 被比较与 ori_dir 异同的文件夹
            move_dir: 如果有重复文件，设定重复文件移动路径，
                      被查找到的与基准文件大小相同，或者文件名类似超过阈值的文件移动到 move_dir
            ismovesamesize:   是否移动相同大小尺寸的文件
            ismovesimlarname: 是否移动相似度为threshold的文件
            threshold:        文件名相似度阈值
        """
        self.ori_name_path_dict = get_name_path_dict(ori_dir)
        self.des_name_path_dict = get_name_path_dict(des_dir)
        self.move_dir = move_dir
        Path(self.move_dir).mkdir(parents=True, exist_ok=True)
        self.ismovesamesize = ismovesamesize
        self.ismovesimlarname = ismovesimlarname
        self.threshold = threshold
        self.isonlyshow = False  # 用于只查看文件对比，不移动文件

    def move_file(self, file_path, move_dir):
        if self.isonlyshow:
            return
        name = Path(file_path).name
        if Path(move_dir, name).exists():
            print(f"--------{move_dir} 中已经存在文件 {name}")
            return
        shutil.move(file_path, move_dir)

    def find_duplicate_files(self):
        """
        查找 重名文件，并且比较文件大小
        Args:
            threshold:        文件名相似度阈值
            ismovesamesize:   是否移动相同大小尺寸的文件
            ismovesimlarname: 是否移动相似度为threshold的文件
        Returns:
        """
        count_size_equal = 0  # 相似度满足阈值，size大小相等的文件数量
        count_name_simlar = 0 # 相似度满足阈值，的文件数量,包含count_size_equal
        for ori_file_name in self.ori_name_path_dict.keys():
            for des_file_name in self.des_name_path_dict.keys():
                # 计算相似度
                similarity_ratio = difflib.SequenceMatcher(None, ori_file_name, des_file_name).quick_ratio()
                if similarity_ratio > self.threshold:
                    ori_file_path = self.ori_name_path_dict[ori_file_name]
                    des_file_path = self.des_name_path_dict[des_file_name]
                    if not Path(des_file_path).exists():
                        continue
                    size_ori = Path(ori_file_path).stat().st_size
                    size_des = Path(des_file_path).stat().st_size
                    parentname_ori = Path(ori_file_path).parent.name
                    parentname_des = Path(des_file_path).parent.name
                    count_name_simlar += 1

                    # 对size相同文件的处理
                    if size_ori == size_des:
                        count_size_equal += 1
                        print("************Same****************")
                        print(f"{parentname_ori}/{ori_file_name}, {size_ori}")
                        print(f"{parentname_des}/{des_file_name}, {size_des}")
                        print("#############################")
                        if self.ismovesamesize:
                            self.move_file(des_file_path, self.move_dir)
                    else:  # 对相似文件的处理
                        print("*************Simlar***************")
                        print(f"{parentname_ori}/{ori_file_name}, {size_ori}")
                        print(f"{parentname_des}/{des_file_name}, {size_des}")
                        print("#############################")
                        if self.ismovesimlarname:
                            self.move_file(des_file_path, self.move_dir)

        print(f"文件名相似度>{self.threshold}, 的文件个数：{count_name_simlar}")
        print(f"文件名相似度>{self.threshold}, 同时size大小相同的文件个数：{count_size_equal}")
        print(f"基准文件个数/被比较文件个数：{len( self.ori_name_path_dict)}/{len(self.des_name_path_dict)}")

    def show_compare_info(self):
        self.isonlyshow = True
        self.find_duplicate_files()
        self.isonlyshow = False


def main_1():
    # 需要被比较，作为基准的文件夹

    dir_ori =  "/home/ytusdc/Nutstore Files/知识星球分享/1_网文学习"
    # 被比较与 ori 异同的文件夹
    dir_des = "/home/ytusdc/Nutstore Files/知识星球分享/星球文档合集2024-10-31"
    # dir_des = r"E:\BaiduNetdiskDownload\0313\神贴补充中"
    # dir_des 中与dir_ori文件size相同的，转移到 dir_samesiz， 方便处理dir_des剩余的文件
    dir_move = "/home/ytusdc/Downloads/same"

    threshold_value = 0.7
    movesamesize = True
    movesimlarname = True

    duplicate_cls = Duplicate(dir_ori, dir_des, dir_move,
                              ismovesamesize=True,
                              ismovesimlarname=False,
                              threshold=threshold_value)
    duplicate_cls.find_duplicate_files()
    # duplicate_cls.show_compare_info()

if __name__ == '__main__':

    main_1()













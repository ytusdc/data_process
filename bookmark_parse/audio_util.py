from pydub import AudioSegment
from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, error, APIC
from mutagen.id3 import TIT2, TALB, TCON, TDRC
from mutagen.id3 import TPE1, TPE2, TRCK, TPOS, COMM, USLT, TCOM, TEXT, TXXX

import shutil
from pathlib import Path
import os

# pip install pydub
# pip install mutagen
# 还要安装ffmpeg库，windows 可能要配置

#音频转换
class AudioConvert:
    def __init__(self):
        pass

    # 获取Flac音频特性
    def getFlacInfo(self, flac_path):
        # 加载FLAC文件
        try:
            flac_metadata = FLAC(flac_path)
        except Exception as e:
            print(f"Error loading file: {e}")
            return
        # 打印主要的元数据标签
        # [标题, 艺术家, 专辑, 流派, 发行年份]
        for key in ['title', 'artist', 'album', 'genre', 'date']:
            # flac_metadata 中， key 不分大小写
            if key in flac_metadata:
                tag = flac_metadata.get(key)[0]
                print(f"{key}: {tag}")

        # 获取其他信息，例如长度（以秒为单位）
        print("Length (seconds):", flac_metadata.info.length)
        # 获取位深度
        print("Bits Per Sample:", flac_metadata.info.bits_per_sample)
        # 获取采样率
        print("Sample Rate:", flac_metadata.info.sample_rate)
        # 获取声道数
        # print("Channels:", flac_metadata.info.channels)

    # 获取Mp3音频特性
    def getMp3Info(self, mp3_path):
        try:
            metadata = EasyID3(mp3_path)
            # 遍历所有标签并打印
            for key in ['title', 'artist', 'album', 'genre', 'date']:
                if key in metadata:
                    tag = metadata.get(key)[0]
                    print(f"{key}: {tag}")
        except Exception as e:
            print(f"Error loading file: {e}")
            return

        # 创建一个MP3对象
        audio = MP3(mp3_path)
        # 打印音频长度（秒）
        print(f"Length (seconds): {audio.info.length} seconds")
        # 打印比特率
        print(f"Bitrate: {audio.info.bitrate // 1000} kbps")
        # 打印采样率
        print(f"Sample Rate: {audio.info.sample_rate} Hz")

    # 获取音频特性，只支持 Flac/Mp3 两种格式音频
    # 默认文件类型没有错误
    def getAudioInfo(self, audio_path):
        suffix = Path(audio_path).suffix
        if suffix.lower() == ".mp3":
            self.getMp3Info(audio_path)
        elif suffix.lower() == ".flac":
            self.getFlacInfo(audio_path)
        else:
            print(f"只支持 Flac/Mp3，两种格式音频，当前音频格式为{suffix}")

        # try:
        #     audio = FLAC(audio_path)
        #     self.getFlacInfo(audio_path)
        #     return
        # except:
        #     try:
        #         audio = MP3(audio_path)
        #         self.getMp3Info(audio_path)
        #         return
        #     except:
        #         print(f"只支持 Flac/Mp3，两种格式音频，当前音频格式为{suffix}")
        #         return
    # 检查音频后缀有没有错
    def check_audio_format(self, audio_path):
        try:
            audio = FLAC(audio_path)
            return 'FLAC'
        except:
            try:
                audio = MP3(audio_path)
                return 'MP3'
            except:
                return 'Unknown'

    # 修改后缀名错误的文件
    def change_audio_suffix(self, audio_dir):
        suffix_ls = ['.mp3', '.flac']
        file_ls = [os.path.join(src_dir, i) for i in os.listdir(src_dir) if os.path.splitext(i)[-1].lower() in suffix_ls]
        for file in file_ls:
            suffix = Path(file).suffix.lower()  # 原始文件名中后缀
            format_type = self.check_audio_format(file)
            if format_type == "Unknown":
                print(f"未知文件类型：{file}")
                continue
            format_type_suffix = str("." + format_type).lower() # 真实的文件类型后缀
            if suffix == format_type_suffix:
                continue
            else:
                new_path = Path(Path(file).parent, Path(file).stem + format_type_suffix)
                if Path(new_path).exists():
                    print(f"文件：{Path(file).name}, 已经存在，请检查")
                    continue
                else:
                    shutil.move(file, new_path)
                    print(f"文件类型错误，更改：{Path(file).name} >>>>>> {Path(new_path).name}")

    # 根据Flac/mp3 中的信息，重新命名文件: 歌名(title)-歌手名(Artist)
    def renameAudioFile(self, audio_path):
        suffix = Path(audio_path).suffix
        if suffix.lower() == ".mp3":
            audio_metadata = EasyID3(audio_path)
        elif suffix.lower() == ".flac":
            audio_metadata = FLAC(audio_path)
        else:
            return
        # metadata 不分大小写
        if 'title' in audio_metadata and "artist" in audio_metadata:
            title_name = audio_metadata["title"][0]
            artist_name = audio_metadata["artist"][0].replace("/", "&")
            newname = title_name + " - " + artist_name + suffix
            rename_path = Path(Path(audio_path).parent, newname)
            if Path(rename_path).exists():
                print(f"文件：{rename_path}， 已存在，请检查")
            else:
                shutil.move(audio_path, str(rename_path))
        else:
            print(f"没有发现文件信息：{audio_path}")

    def modify_mp3_info(self, mp3_path):
        # 加载MP3文件
        audio = EasyID3(mp3_path)
        # 设置或修改元数据标签
        audio['title'] = 'Your Song Title' # 标题
        audio['artist'] = 'Artist Name' # 艺术家
        audio['album'] = 'Album Name' # 专辑
        audio['genre'] = 'Genre Name' # 流派
        audio['date'] = '2023'  # 年份
        # 保存更改
        audio.save()

        # # 如果需要添加更详细的ID3标签，可以使用ID3类
        # audio_id3 = ID3(mp3_path)
        # # 添加或修改特定的ID3帧
        # audio_id3.add(TIT2(encoding=3, text='Your Song Title'))  # 标题
        # audio_id3.add(TPE1(encoding=3, text='Artist Name'))  # 艺术家
        # audio_id3.add(TALB(encoding=3, text='Album Name'))  # 专辑
        # audio_id3.add(TCON(encoding=3, text='Genre Name'))  # 流派
        # audio_id3.add(TDRC(encoding=3, text='2023'))  # 发行年份
        # # 保存更改
        # audio_id3.save()

    def convert_flac_to_mp3(self, flac_path, mp3_path, bit_rate=None):
        """
        Flac 转 Mp3 文件，同时复制封面图片
        Args:
            flac_path:
            mp3_path:
            bit_rate: 例如'128k', '256k', '320k'

        比特率选择：常见的MP3比特率有 128 kbps、192 kbps、256 kbps 和 320 kbps。
            较高的比特率通常意味着更好的音质，但文件也会更大。
        质量损失：请注意，重新编码音频会引入一些质量损失，即使你提高比特率也是如此。
            因此，最好从原始无损音频源（如FLAC）转换到MP3，以获得最佳音质。
        Returns:
        """
        # 加载FLAC文件
        flac_audio = AudioSegment.from_file(flac_path, format="flac")
        # 导出为MP3文件
        if bit_rate is None:
            # 默认 '128k'
            flac_audio.export(mp3_path, format="mp3")
        else:
            flac_audio.export(mp3_path, format="mp3", bitrate=bit_rate)

        # 读取FLAC文件的元数据
        flac_metadata = FLAC(flac_path)

        # 复制 flac 其他元数据标签
        try:
            mp3_tags = ID3(mp3_path)
        except error:
            # 创建新的ID3标签
            mp3_tags = ID3()

        # 定义标签映射，将FLAC标签转换为ID3标签
        tag_mapping = {
            'title': TIT2,  # 标题
            'artist': TPE1, # 艺术家
            'album': TALB,  # 专辑
            'genre': TCON,  # 流派
            'date': TDRC,   # 发行年份
            # 'albumartist': TPE2,
            # 'tracknumber': TRCK,
            # 'discnumber': TPOS,
            # 'comment': COMM,
            # 'lyrics': USLT,
            # 'composer': TCOM,
            # 'lyricist': TEXT,
        }

        for key, value in flac_metadata.items():
            if key in tag_mapping:
                tag_class = tag_mapping[key]
                if isinstance(value, list):
                    value = value[0]  # 只取第一个值
                mp3_tags.add(tag_class(encoding=3, text=str(value)))

        # 尝试从原始文件中提取封面图片
        for tag in flac_metadata.pictures:
            if tag.type == 3:  # 前封面
                # 添加封面图片到新文件中
                new_apic = APIC(
                    encoding=3,  # UTF-8
                    mime=tag.mime,  # MIME类型
                    type=3,  # 前封面
                    desc=u'Cover',
                    data=tag.data
                )
                mp3_tags.add(new_apic)
                # print("Cover image copied successfully.")
                break
        else:
            # print("No cover image found in the original file.")
            pass

        # 保存新的ID3标签到输出文件
        mp3_tags.save(mp3_path)

    def convert_flac_to_mp3_simple(self, flac_path, mp3_path, bit_rate=None):
        """
         Flac 转 Mp3 文件， 只复制相关信息
        使用 EasyID3 简单接口
        Args:
            flac_path:
            mp3_path:
            bit_rate: 例如'128k', '256k', '320k'

        比特率选择：常见的MP3比特率有 128 kbps、192 kbps、256 kbps 和 320 kbps。
            较高的比特率通常意味着更好的音质，但文件也会更大。
        质量损失：请注意，重新编码音频会引入一些质量损失，即使你提高比特率也是如此。
            因此，最好从原始无损音频源（如FLAC）转换到MP3，以获得最佳音质。
        Returns:
        """
        # 加载FLAC文件
        flac_audio = AudioSegment.from_file(flac_path, format="flac")
        # 导出为MP3文件
        if bit_rate is None:
            # 默认 '128k'
            flac_audio.export(mp3_path, format="mp3")
        else:
            flac_audio.export(mp3_path, format="mp3", bitrate=bit_rate)

        # 读取FLAC文件的元数据
        flac_metadata = FLAC(flac_path)
        # 加载MP3文件以设置元数据
        try:
            mp3_metadata = EasyID3(mp3_path)
        except Exception:
            mp3_metadata = EasyID3()
            print(f"获取mp3文件报错：{mp3_path}")
            return
        # 将FLAC元数据复制到MP3文件
        for key in ['title', 'artist', 'album', 'genre', 'date']:
            if key in flac_metadata:
                mp3_metadata[key] = flac_metadata[key]
        # 保存MP3文件的元数据到MP3文件
        mp3_metadata.save(mp3_path)

    def change_mp3_bitrate(self, input_file, output_file, bit_rate):
        """
        MP3文件更改码率，同时复制封面
        Args:
            input_file:
            output_file:
            bit_rate: 例如'128k', '256k', '320k'
        Returns:
        """
        # 加载MP3文件
        audio = AudioSegment.from_mp3(input_file)
        # 设置新的比特率（单位是 kbps）
        new_audio = audio.export(output_file, format="mp3", bitrate=bit_rate)
        print(f"File has been converted to {bit_rate} kbps and saved as {output_file}")

        # 读取原始文件的ID3标签
        try:
            original_tags = ID3(input_file)
        except error:
            print("No ID3 tags found in the original file.")
            return
        try:
            new_tags = ID3(output_file)
        except error:
            new_tags = ID3()

        # 复制所有其他ID3标签
        for key in original_tags.keys():
            if key != 'APIC':  # 已经处理过封面图片
                for tag in original_tags.getall(key):
                    new_tags.add(tag)

        # 尝试从原始文件中提取封面图片
        for tag in original_tags.getall('APIC'):
            if isinstance(tag, APIC):
                # 将封面图片添加到新文件中
                new_tags.add(tag)
                # new_tags.save(output_file)
                # print("Cover image copied successfully.")
                break
        new_tags.save(output_file)

# 单独转换一个flac文件到mp3
def main_convert_2_mp3(flac_path):
    audioConvert_cls = AudioConvert()
    mp3_name = Path(flac_path).stem + '.mp3'
    mp3_path = Path(Path(flac_path).parent, mp3_name)
    audioConvert_cls.convert_flac_to_mp3(flac_path, mp3_path)

# 文件根据信息重命名
def main_rename(src_dir):
    audioConvert_cls = AudioConvert()
    audioConvert_cls.change_audio_suffix(src_dir)
    suffix = ['.mp3', '.flac']
    file_ls = [os.path.join(src_dir, i) for i in os.listdir(src_dir) if os.path.splitext(i)[-1].lower() in suffix]
    for file in sorted(file_ls):
        audioConvert_cls.renameAudioFile(file)
# 转换目录下的flac，到mp3
def main_convert(src_dir):
    audioConvert_cls = AudioConvert()
    audioConvert_cls.change_audio_suffix(src_dir)

    suffix = ['.flac']
    file_ls = [os.path.join(src_dir, i) for i in os.listdir(src_dir) if os.path.splitext(i)[-1].lower() in suffix]
    for flac_file in sorted(file_ls):
        mp3_name = Path(flac_file).stem + '.mp3'
        mp3_path = Path(Path(flac_file).parent, mp3_name)
        audioConvert_cls.convert_flac_to_mp3(flac_file, mp3_path)

if __name__ == '__main__':

    flac_file = "/home/ytusdc/Downloads/人间烟火-程响.flac"
    mp3_file = "/home/ytusdc/Downloads/人间烟火-程响.mp3"
    src_dir = "/home/ytusdc/Downloads/test/"
    mp3_file = "/home/ytusdc/Downloads/赵乃吉-曾经你说.mp3"
    mp3_file = "/home/ytusdc/Downloads/test/体面 - 于文文.mp3"

    temp = "/home/ytusdc/Downloads/test/陈一发儿 - 童话镇.mp3"
    temp = "/home/ytusdc/Downloads/1_music/不仅仅是喜欢 - 孙语赛.mp3"

    main_convert_2_mp3("/home/ytusdc/Downloads/11/W2L.BHY/00.mp3")

    # main_convert(src_dir)
    # main_rename(temp)
    # audioConvert_cls = AudioConvert()
    #
    # audioConvert_cls.getAudioInfo(temp)


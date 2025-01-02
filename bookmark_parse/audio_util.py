from pydub import AudioSegment
from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON, TDRC
import shutil
from pathlib import Path
import os

# pip install pydub
# pip install mutagen

#音频转换
class AudioConvert:
    def __init__(self):
        pass

    def getFlacInfo(self, flac_path):
        # 加载FLAC文件
        flac_metadata = FLAC(flac_path)
        # 打印所有元数据标签
        print(flac_metadata.tags)
        # 获取特定标签信息
        if 'TITLE' in flac_metadata:   # 标题
            print("Title:", flac_metadata['TITLE'][0])
        if 'ARTIST' in flac_metadata:  # 艺术家
            print("Artist:", flac_metadata['ARTIST'][0])
        if 'ALBUM' in flac_metadata:   # 专辑
            print("Album:", flac_metadata['ALBUM'][0])
        if 'DATE' in flac_metadata:    # 发行年份
            print("Date:", flac_metadata['DATE'][0])
        if 'GENRE' in flac_metadata:   # 流派
            print("Genre:", flac_metadata['GENRE'][0])
        # 获取其他信息，例如长度（以秒为单位）
        print("Length (seconds):", flac_metadata.info.length)
        # 获取采样率
        print("Sample Rate:", flac_metadata.info.sample_rate)
        # 获取位深度
        print("Bits Per Sample:", flac_metadata.info.bits_per_sample)
        # 获取声道数
        print("Channels:", flac_metadata.info.channels)

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
            artist_name = audio_metadata["artist"][0]
            newname = title_name + "-" + artist_name + suffix
            rename_path = Path(Path(audio_path).parent, newname)
            shutil.move(audio_path, str(rename_path))
        else:
            print(f"没有发现文件信息：{audio_path}")


    def modify_mp3_info(self, mp3_path):
        # 加载MP3文件
        audio = EasyID3(mp3_path)
        # 设置或修改元数据标签
        audio['title'] = 'Your Song Title'
        audio['artist'] = 'Artist Name'
        audio['album'] = 'Album Name'
        audio['genre'] = 'Genre Name'
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

    def convert_flac_to_mp3(self, flac_path, mp3_path, bit_rate='320k'):
        # 加载FLAC文件
        flac_audio = AudioSegment.from_file(flac_path, format="flac")
        # 导出为MP3文件
        # flac_audio.export(mp3_path, format="mp3", bitrate="320k")
        flac_audio.export(mp3_path, format="mp3")

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


# 单独转换一个flac文件到mp3
def main_convert_2_mp3(flac_path):
    audioConvert_cls = AudioConvert()
    mp3_name = Path(flac_path).stem + '.mp3'
    mp3_path = Path(Path(flac_path).parent, mp3_name)
    audioConvert_cls.convert_flac_to_mp3(flac_path, mp3_path)

# 文件根据信息重命名
def main_rename(src_dir):
    suffix = ['.mp3', '.flac']
    file_ls = [os.path.join(src_dir, i) for i in os.listdir(src_dir) if os.path.splitext(i)[-1].lower() in suffix]

    audioConvert_cls = AudioConvert()
    for file in file_ls:
        audioConvert_cls.renameAudioFile(file)
# 转换目录下的flac，到mp3
def main_convert(src_dir):
    suffix = ['.flac']
    file_ls = [os.path.join(src_dir, i) for i in os.listdir(src_dir) if os.path.splitext(i)[-1].lower() in suffix]
    audioConvert_cls = AudioConvert()
    for flac_file in file_ls:
        mp3_name = Path(flac_file).stem + '.mp3'
        mp3_path = Path(Path(flac_file).parent, mp3_name)
        audioConvert_cls.convert_flac_to_mp3(flac_file, mp3_path)


if __name__ == '__main__':

    flac_file = "/home/ytusdc/Downloads/人间烟火-程响.flac"
    mp3_file = "/home/ytusdc/Downloads/人间烟火-程响.mp3"

    src_dir = ""
    main_convert(src_dir)



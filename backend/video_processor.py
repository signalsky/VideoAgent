from moviepy import VideoFileClip
import subprocess
import os
from pathlib import Path


def extract_vocal(video_path, name):
    """
    提取视频中的人声（依赖 spleeter 和 ffmpeg）
    :param video_path: 输入视频路径
    :param output_video_path: 输出去人声的视频
    """
    temp_audio = f"{name}_audio.mp3"
    output_dir = os.path.dirname(video_path)
    
    # 使用 with 语句自动管理资源
    with VideoFileClip(video_path) as video:
        video.audio.write_audiofile(temp_audio)
    
    # 分离人声
    subprocess.run([
        "spleeter", "separate",
        "-p", "spleeter:2stems",
        "-o", output_dir,
        "-c", "mp3",  # 指定输出为 MP3 格式
        temp_audio
    ], check=True)
    
    # 获取人声文件路径
    base_name = os.path.splitext(os.path.basename(temp_audio))[0]
    vocal_path = os.path.join(output_dir, base_name, "vocals.mp3")
    accompaniment_path = os.path.join(output_dir, base_name, "accompaniment.mp3")
    os.remove(temp_audio) # 删除临时音频文件
    return vocal_path, accompaniment_path


def process_video(video_path):
    path_obj = Path(video_path)
    # 提取音频
    audio_output_path, accompaniment_path = extract_vocal(video_path, path_obj.stem)
    print(f"音频已提取到 {audio_output_path}")
    print(f"背景音乐已提取到 {accompaniment_path}")
    return audio_output_path, accompaniment_path


def merge_media(
    input_video: str,    # 无人声的视频文件路径
    input_audio: str,    # 需要合并的音频文件路径
    accompaniment_path: str, # 背景音乐
    input_subtitle: str, # 字幕文件路径 (支持.srt/.ass)
    output_path: str,    # 输出文件路径
) -> None:
    """
    四合一媒体合并函数
    """
    temp_path = output_path.replace("_cn.", "_temp.")
    merge_audio_video(input_video, input_audio, accompaniment_path, temp_path)
    merge_video_with_subtitles(temp_path, input_subtitle, output_path)
    os.remove(temp_path)
    


def merge_audio_video(
    input_video: str,    # 视频文件路径
    input_audio: str,    # 音频文件路径
    accompaniment_path,  # 背景音乐路径
    output_path: str     # 输出文件路径
) -> None:
    """
    合并音频和视频的函数
    """

    print("开始合并音频和视频")

    # 输入文件校验
    for path in [input_video, input_audio, accompaniment_path]:
        if not Path(path).exists():
            raise FileNotFoundError(f"输入文件不存在: {path}")
    
    # FFmpeg 复杂滤镜配置
    filter_complex = (
        "[1:a]volume=1.0[bg];"    # 背景音乐保持原音量
        "[2:a]volume=1.0[vocal];" # 人声保持原音量
        "[bg][vocal]amix=inputs=2:duration=longest[aout]"  # 混合两个音频
    )

    # FFmpeg 命令
    cmd = [
        "ffmpeg",
        "-y",
        "-i", input_video,         # 输入0：视频文件
        "-i", accompaniment_path,  # 输入1：背景音乐
        "-i", input_audio,         # 输入2：人声音频
        "-filter_complex", filter_complex,
        "-map", "0:v",             # 选择视频流
        "-map", "[aout]",          # 选择混合后的音频
        "-c:v", "copy",            # 复制视频流
        "-c:a", "aac",             # AAC音频编码
        "-q:a", "1",               # 音频质量（1=最高质量）
        output_path
    ]

    # 执行命令
    try:
        subprocess.run(
            cmd,
            check=True,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        print(f"合并成功！输出文件: {output_path}")
    except subprocess.CalledProcessError as e:
        print("合并失败，错误信息:")
        print(e.stderr)
        raise

def merge_video_with_subtitles(input_video, input_subtitles, output_video):
    try:
        command = [
            'ffmpeg',
            "-y",  # 覆盖已存在文件
            '-i', input_video,
            '-vf', f'subtitles={input_subtitles}',
            '-c:v', 'libx264',
            '-crf', '23',
            '-preset', 'slow',
            '-c:a', 'copy',
            output_video
        ]
        subprocess.run(command, check=True)
        print(f"视频和字幕合并成功，输出文件为 {output_video}")
    except subprocess.CalledProcessError as e:
        print(f"合并过程中出现错误: {e}")
    except FileNotFoundError:
        print("未找到 ffmpeg 命令，请确保 ffmpeg 已正确安装并配置到系统环境变量中。")


if __name__ == "__main__":
    # process_video("downloads/GAoR9ji8D6A/GAoR9ji8D6A.mp4")
    merge_media("downloads/GAoR9ji8D6A/GAoR9ji8D6A.mp4",            
                "./downloads/GAoR9ji8D6A/GAoR9ji8D6A_audio/cn.mp3",
                "./downloads/GAoR9ji8D6A/GAoR9ji8D6A_audio/accompaniment.mp3",
                "./downloads/GAoR9ji8D6A/subtitles.srt",
                "./downloads/GAoR9ji8D6A/GAoR9ji8D6A_cn.mp4")


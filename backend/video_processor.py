from moviepy import VideoFileClip
import subprocess
import os
from pathlib import Path


def extract_vocal(video_path, output_video_path, name):
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
    subprocess.run([
        "ffmpeg",
        "-y",  # 强制覆盖输出文件
        "-i", video_path,
        "-i", accompaniment_path,
        "-map", "0:v",  # 原视频画面
        "-map", "1:a",  # 伴奏音频
        "-map", "-0:s",  # 排除原视频的所有字幕轨道
        "-c:v", "copy",  # 不重新编码视频
        "-c:a", "aac",   # 音频编码格式
        output_video_path
    ], check=True)

    os.remove(temp_audio) # 删除临时音频文件
    return vocal_path



def process_video(video_path):
    path_obj = Path(video_path)
    video_no_subtitle_no_vocal_output_path = path_obj.parent / f"{path_obj.stem}_no_subtitle_no_vocal.mp4"
    # 提取音频
    audio_output_path = extract_vocal(video_path, video_no_subtitle_no_vocal_output_path, path_obj.stem)
    print(f"音频已提取到 {audio_output_path}")
    print(f"视频去除人声 {video_no_subtitle_no_vocal_output_path}")
    return video_no_subtitle_no_vocal_output_path, audio_output_path


def merge_media(
    input_video: str,    # 无人声的视频文件路径
    input_audio: str,    # 需要合并的音频文件路径
    input_subtitle: str, # 字幕文件路径 (支持.srt/.ass)
    output_path: str,    # 输出文件路径
    resolution: str = "libx264",  # 输出分辨率，例如 "1920x1080" 或 "copy"
    crf: int = 23            # 视频质量参数 (0-51, 越小质量越高)
) -> None:
    """
    三合一媒体合并函数
    """

    print("视频、音频、字幕三合一")
    
    # 输入文件校验
    for path in [input_video, input_audio, input_subtitle]:
        if not Path(path).exists():
            raise FileNotFoundError(f"输入文件不存在: {path}")
    
    # FFmpeg 基础命令
    cmd = [
        "ffmpeg",
        "-y",  # 覆盖已存在文件
        "-i", input_video,
        "-i", input_audio,
    ]
    
    # 字幕处理参数
    subtitle_filter = f"subtitles='{input_subtitle}'"
    
    # 视频处理滤镜链
    filter_complex = [
        "[0:v] " + subtitle_filter + " [v]",  # 视频流叠加字幕
        "[1:a] apad [a]"                     # 音频流填充静音保证对齐
    ]
    
    # 构建完整命令
    cmd += [
        "-filter_complex", "; ".join(filter_complex),
        "-map", "[v]",
        "-map", "[a]",
        "-c:v", resolution,
        "-crf", str(crf),
        "-preset", "medium",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest"  # 以最短的流为准
    ]
    
    # 分辨率设置
    # if resolution != "copy":
    #     cmd += ["-s", resolution]
    
    cmd += [output_path]
    
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


if __name__ == "__main__":
    # process_video("downloads/GAoR9ji8D6A/GAoR9ji8D6A.mp4")
    merge_media("downloads/GAoR9ji8D6A/GAoR9ji8D6A.mp4",            
                "./downloads/GAoR9ji8D6A/GAoR9ji8D6A_audio/cn.mp3",
                "./downloads/GAoR9ji8D6A/subtitles.srt",
                "./downloads/GAoR9ji8D6A/GAoR9ji8D6A_cn.mp4")

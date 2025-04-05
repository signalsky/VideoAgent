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



if __name__ == "__main__":
    process_video("downloads/GAoR9ji8D6A/GAoR9ji8D6A.mp4")

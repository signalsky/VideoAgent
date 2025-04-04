from moviepy import VideoFileClip
import subprocess
import os
from pathlib import Path


def extract_audio(video_path, output_audio_path):
    """
    从视频中提取音频
    :param video_path: 输入视频的路径
    :param output_audio_path: 输出音频的路径
    """
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(output_audio_path)
    audio.close()
    video.close()


def remove_subtitles_and_audio(video_path, output_video_path):
    """
    移除视频中的字幕和音频
    :param video_path: 输入视频的路径
    :param output_video_path: 输出无字幕无音频视频的路径
    """
    command = [
        'ffmpeg',
        '-i', video_path,
        '-an',  # 移除音频
        '-map', '0:v',  # 只选择视频流
        '-c:v', 'copy',  # 直接复制视频流，不进行重新编码
        output_video_path
    ]
    subprocess.run(command, check=True)


def process_video(video_path):
    path_obj = Path(video_path)
    audio_output_path = path_obj.parent / f"{path_obj.stem}_audio.mp3"
    video_no_subtitle_no_audio_output_path = path_obj.parent / f"{path_obj.stem}_no_subtitle_no_audio.mp4"

    # 提取音频
    extract_audio(video_path, audio_output_path)
    print(f"音频已提取到 {audio_output_path}")

    # 移除字幕和音频
    remove_subtitles_and_audio(video_path, video_no_subtitle_no_audio_output_path)
    print(f"无字幕无音频视频已保存到 {video_no_subtitle_no_audio_output_path}")
    return audio_output_path, video_no_subtitle_no_audio_output_path


if __name__ == "__main__":
    process_video("downloads/GAoR9ji8D6A.mp4")

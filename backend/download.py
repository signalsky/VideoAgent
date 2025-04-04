import os
from pathlib import Path
import yt_dlp
import platform
from urllib.parse import urlparse, parse_qs

system_name = platform.system()
if system_name == 'Windows':
    DOWNLOAD_DIR = 'downloads'
else:
    DOWNLOAD_DIR = "downloads"


def get_youtube_video_id(youtube_url):
    # 解析URL
    parsed_url = urlparse(youtube_url)
    # 从查询参数中获取视频ID
    video_id = parse_qs(parsed_url.query).get('v')
    if video_id:
        return video_id[0]
    return None


async def download_youtube_video(youtube_url):
    video_id = get_youtube_video_id(youtube_url)
    base_path = Path(DOWNLOAD_DIR) / video_id
    base_path.mkdir(parents=True, exist_ok=True)
    full_path = base_path / video_id
    ydl_opts = {
        'outtmpl':str(full_path),
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4'
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.download([youtube_url])
        if result == 0:
            return f'/downloads/{video_id}/{video_id}.mp4', result
        else:
            return '', result


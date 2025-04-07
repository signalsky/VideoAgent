import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from download import DOWNLOAD_DIR, download_youtube_video
from video_processor import process_video, merge_media
from ai import audio_to_txt

# 创建 FastAPI 实例并添加自定义配置
app = FastAPI(
    title="视频处理 API",
    description="这是一个用于处理 YouTube 视频的 API，包括下载、处理和合并等功能。",
    version="1.0.0"
)

# 定义视频保存的目录
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

# 挂载静态文件目录，这样可以通过 /downloads 路径访问下载的视频
app.mount("/downloads", StaticFiles(directory=DOWNLOAD_DIR), name="downloads")


class VideoRequest(BaseModel):
    youtube_url: str
    

@app.post("/trans_vedio")
async def trans_video(request: VideoRequest):
    try:
        if not request.youtube_url.startswith('https://www.youtube.com'):
            youtube_url = f'https://www.youtube.com/watch?v={request.youtube_url}'
        else:
            youtube_url = request.youtube_url
        video_path, video_id, status = await download_youtube_video(youtube_url)
        audio_output_path, accompaniment_path = process_video(video_path)
        srt_file = os.path.join(os.path.dirname(video_path), 'subtitles.srt')
        audio_cn = os.path.join(os.path.dirname(audio_output_path), 'cn.mp3')
        audio_to_txt(audio_output_path, srt_file, audio_cn)
        output_path = os.path.join(os.path.dirname(video_path), f'{video_id}_cn.mp4')
        merge_media(video_path, audio_cn, accompaniment_path, srt_file, output_path)
        return {
            "status": status,
            "file_link": f'/downloads/{video_id}/{video_id}_cn.mp4',
            "message": "视频下载成功" if status == 0 else "视频下载失败"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"视频下载失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3141)

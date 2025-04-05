import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from download import DOWNLOAD_DIR, download_youtube_video
from video_processor import process_video
from ai import audio_to_txt

app = FastAPI()

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
        video_path, status = await download_youtube_video(youtube_url)
        video_no_subtitle_no_vocal_output_path, audio_output_path = process_video(video_path)
        srt_file = os.path.join(os.path.dirname(video_path), 'subtitles.srt')
        audio_cn = os.path.join(os.path.dirname(audio_output_path), 'cn.mp3')
        audio_to_txt(audio_output_path, srt_file, audio_cn)
        return {
            "status": status,
            "file_link": '',
            "message": "视频下载成功" if status == 0 else "视频下载失败"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"视频下载失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3141)

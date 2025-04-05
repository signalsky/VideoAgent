import io
from pydub import AudioSegment
from openai import OpenAI


def audio_to_txt(original_audio_file, srt_file, cn_audio_file):
    print("开始语音转文字...")
    client = OpenAI(api_key="")
    with open(original_audio_file, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            response_format="verbose_json",
            prompt="Please split the segments according to complete sentences to avoid having a single sentence divided among multiple segments.",
            timestamp_granularities=["segment"]
        )
    print("语音转文字结束!")

    # 提取段落时间戳
    print("开始中文翻译...")
    srt_list = []
    for segment in transcript.segments:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            timeout=60,
            temperature=0.3, # 平衡准确性与术语灵活性
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业翻译, 请将输入的英文翻译为专业简体中文, 直接翻译不用解释, 即使只有一个单词, 也不用解释",
                },
                {
                    "role": "user",
                    "content": segment.text
                }
            ]
        )
        print(f"处理文字：{segment.start} - {segment.end} : {segment.text}")
        srt_list.append((segment.start, segment.end, response.choices[0].message.content))
    print("中文翻译结束!")
    generate_audio(client, srt_list, cn_audio_file)
    generate_srt(srt_list, srt_file)
    

def process_srt_list(srt_list):
    result = []
    current_start = None
    current_end = None
    current_text = ""
    current_duration = 0

    for start, end, text in srt_list:
        if current_start is None:
            current_start = start

        current_text += text
        current_end = end
        current_duration += end - start

        if current_duration >= 45:
            result.append((current_start, current_end, current_text))
            current_start = None
            current_text = ""
            current_duration = 0

    # 处理最后一组未达到 1 分钟的字幕
    if current_start is not None:
        result.append((current_start, current_end, current_text))

    return result

def generate_audio(client, srt_list, cn_audio_file):
    print("生成中文语音...")
    new_list = process_srt_list(srt_list)
    total_len = 0
    cn_audio = AudioSegment.empty()
    for start, end, text in new_list:
        print(total_len, start, end, text)
        if total_len < start * 1000:
            cn_audio += AudioSegment.silent(start * 1000 - total_len)
            total_len = len(cn_audio)
            print(total_len)
        response2 = client.audio.speech.create(
            model="tts-1-hd",
            voice="nova",
            response_format = "mp3",
            input=text
        )
        raw_audio = AudioSegment.from_file(io.BytesIO(response2.content), format="mp3")
        cn_audio += raw_audio
        print(len(raw_audio))
        total_len += len(raw_audio)
    cn_audio.export(cn_audio_file, format="mp3")


def format_time(seconds):
    """
    将秒转换为 SRT 格式的时间字符串
    :param seconds: 秒数
    :return: SRT 格式的时间字符串
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def generate_srt(input_list, output_file):
    """
    生成 SRT 字幕文件
    :param input_list: 输入的时间和文本元组列表
    :param output_file: 输出的 SRT 文件路径
    """
    print("生成字幕...")
    print(input_list)
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, (start, end, text) in enumerate(input_list, start=1):
            start_time = format_time(start)
            end_time = format_time(end)
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text}\n\n")
    print("字幕生成完成!")


if __name__ == "__main__":
    audio_to_txt("./downloads/GAoR9ji8D6A/GAoR9ji8D6A_audio/vocals.mp3", 
                 "./downloads/GAoR9ji8D6A/subtitles.srt",
                 "./downloads/GAoR9ji8D6A/GAoR9ji8D6A_audio/cn.mp3")

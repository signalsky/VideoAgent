from openai import OpenAI


def audio_to_txt(original_audio_file):
    client = OpenAI(api_key="")
    with open(original_audio_file, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            response_format="verbose_json",
            timestamp_granularities=["segment"]
        )

    # 提取段落时间戳
    for segment in transcript.segments:
        print(segment)
        print(f"文本: {segment.text}")
        print(f"开始: {segment.start}, 结束: {segment.end}\n")


    # response = client.chat.completions.create(
    #     model="gpt-4",
    #     messages=[
    #         {"role": "system", "content": "分析以下文本的情绪（如愤怒、快乐、中性等）："},
    #         {"role": "user", "content": text}
    #     ]
    # )
    # emotion = response.choices[0].message.content
    # print(emotion)


if __name__ == "__main__":
    audio_to_txt("./downloads/GAoR9ji8D6A_audio.mp3")

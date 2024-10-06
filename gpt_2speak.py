import openai
import requests
import json
import io
import wave
import pyaudio
import time

gpt_count = 0
assistant_response = ""  # 一時リセット
openai.api_key = ''#apiキー

# 会話履歴を保持するリスト
messages = [
    {"role": "system", "content": " #あなたは17歳の女の子です。四国めたん"},
    {"role": "system", "content": " #あなたはずんだのようせいずんだもんです"}
]

def chat_with_gpt(user_input):
    global gpt_count  
    global assistant_response  

    # ユーザーの入力を履歴に追加
    messages.append({"role": "user", "content": user_input})

    # GPT-3.5 Turboにリクエストを送信
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    # GPTの返答を履歴に追加
    assistant_response = response.choices[0].message.content
    messages.append({"role": "assistant", "content": assistant_response})

    gpt_count += 1  # gpt_countを増加させる
    return assistant_response

### Voicevoxクラス
class Voicevox:
    def __init__(self, host="127.0.0.1", port=50021):
        self.host = host
        self.port = port

    def speak(self, text=None):
        if gpt_count %2== 1:
            speaker = 7  # めたん
        elif gpt_count % 2 == 0:
            speaker = 6  # ずんだもん
        

        params = (
            ("text", text),
            ("speaker", speaker)  # 音声の種類をInt型で指定
        )

        init_q = requests.post(
            f"http://{self.host}:{self.port}/audio_query",
            params=params
        )

        res = requests.post(
            f"http://{self.host}:{self.port}/synthesis",
            headers={"Content-Type": "application/json"},
            params=params,
            data=json.dumps(init_q.json())
        )

        # メモリ上で展開
        audio = io.BytesIO(res.content)

        with wave.open(audio, 'rb') as f:
            p = pyaudio.PyAudio()

            def _callback(in_data, frame_count, time_info, status):
                data = f.readframes(frame_count)
                return (data, pyaudio.paContinue)

            stream = p.open(format=p.get_format_from_width(width=f.getsampwidth()),
                            channels=f.getnchannels(),
                            rate=f.getframerate(),
                            output=True,
                            stream_callback=_callback)

            # Voice再生
            stream.start_stream()
            while stream.is_active():
                time.sleep(0.1)

            stream.stop_stream()
            stream.close()
            p.terminate()

# ユーザー入力を受け取り、関数を呼び出すループ
while gpt_count < 10:
    if gpt_count == 0:
        user_input = input("最初のお題: ")
        response = chat_with_gpt(user_input)
        print(f"ずんだもん: {response}")
    else:
        response = chat_with_gpt(assistant_response)
        print(f"めたん: {response}")

    # 音声合成を呼び出す
    vv = Voicevox()
    vv.speak(response)

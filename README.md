## 基於 Edge TTS Worker 的 epub 有聲書實作
Edge TTS Worker 是一個部署在 Cloudflare Worker 上的代理服務，它將微軟 Edge TTS 服務封裝成兼容 OpenAI 格式的 API 接口。通過本項目，您可以在沒有微軟認證的情況下，輕松使用微軟高質量的語音合成服務。

https://github.com/linshenkx/edge-tts-openai-cf-worker/tree/master

建置 edge tts service 後，用它來幫 epub 電子書產生 MP3 有聲書。
[list of voices available in Edge TTS](https://gist.github.com/BettyJJ/17cbaa1de96235a7f5773b8690a20462)

```python
client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

#_VOICE_INDEX = 0  #"zh-TW-YunJheNeural"
_VOICE_INDEX = 2  #"en-US-ChristopherNeural"

def tts_service(text, output_path):
    """
    Generate MP3 audio file from text

    Parameters:
      text(str): text to get audio
      output_path(str): the pathname of audiofile
    """
    data = {
      'model': 'tts-1',
      'input': 'sample',
      'voice': 'en-US-ChristopherNeural',
      'response_format': 'mp3',
      'speed': 1.0,
    }
    # Update the input text
    data['input'] = text
    # Modify the 'voice'
    data['voice'] = voicedata.voices[_VOICE_INDEX]["ShortName"]
    # Adjust the 'speed'
    data['speed'] = 1.0
    try:
        response = client.audio.speech.create(
          **data
        )
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f'MP3 file saved successfully to {output_path}')

    except Exception as e:
        print(f"An error occurred: {e}")
```

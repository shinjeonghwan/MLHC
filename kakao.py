import requests
import json
kakao_speech_url = "https://kakaoi-newtone-openapi.kakao.com/v1/recognize"

rest_api_key = 'a0b818404883532ce93da157ad839f89'

headers = {
    "Content-Type": "application/octet-stream",
    "X-DSS-Service": "DICTATION",
    "Authorization": "KakaoAK " + rest_api_key,
}

with open('test.pcm', 'rb') as fp:
    audio = fp.read()

res = requests.post(kakao_speech_url, headers=headers, data=audio)
print(res)
print(type(res))

result_json_string = res.text[res.text.index('{"type":"finalResult"'):res.text.rindex('}')+1]
result = json.loads(result_json_string)
print(result)
print(result['value'])

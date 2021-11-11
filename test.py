import boto3
import json

comprehend = boto3.client(service_name = 'comprehend', region_name = 'us-east-1')

text = "테스트 중 치킨이랑 맥주먹고싶다 시발 아침에 눈을 뜨면 콩깍지콩쥐 팥쥐"
json_keyword = comprehend.detect_key_phrases(Text=text, LanguageCode='ko')

print(comprehend.detect_key_phrases(Text=text, LanguageCode='ko'))
print(json_keyword['KeyPhrases'][0]['Text'])
print(comprehend.detect_key_phrases(Text=text, LanguageCode='ko')['KeyPhrases'][1]['Text'])
print(comprehend.detect_key_phrases(Text=text, LanguageCode='ko')['KeyPhrases'][2]['Text'])

print(len(json_keyword))

for i in json_keyword['KeyPhrases']:
    print(i['Text'])

from pororo import Pororo
import pandas as pd
import boto3
import requests
import json
from gensim.models import FastText as FT
import datetime
import numpy as np
from konlpy.tag import Okt
import random
okt=Okt()

#Amazon comprehend API 활성화
#comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')

print("주제 추출 알고리즘")
zsl = Pororo(task="zero-topic", lang="ko")

test = zsl("시켜서 먹자 치킨은 두마리 같이먹자 집에 가자 아침에 집에 가자 알았지 그리고 먹는 김에 치즈볼도 아 치킨먹고싶다",["식사","음식","의류"])


print("시켜서 먹자 치킨은 두마리 같이먹자 집에 가자 아침에 집에 가자 알았지 그리고 먹는 김에 치즈볼도 아 치킨먹고싶다")
#print(zsl("나가서 뜨끈한 국밥 한그릇하자",["식사","스포츠","의류"]))
print(test)

max = 0
main_keyword = []
for main in test:
    if test[main] > max:
        max = test[main]
        main_keyword = main

print(main_keyword)


import boto3
import json
import requests
import os


from pororo import Pororo
import pandas as pd
import requests
import json
from gensim.models import FastText as FT
import datetime
import numpy as np
from konlpy.tag import Okt
import random
okt=Okt()



def string_to_keyword(string):
    keywords = []

    comprehend = boto3.client(service_name = 'comprehend', region_name = 'us-east-1')
    json_keyword = comprehend.detect_key_phrases(Text=string, LanguageCode='ko')['KeyPhrases']

    text= []
    score= []
    BeginOffset = []
    EndOffset = []
    for key in json_keyword:
        text.append(key["Text"]) # 조금 더 정확한 유의어 출력을 위한 공백 제거
        score.append(str(key["Score"]))
        BeginOffset.append(str(key["BeginOffset"]))
        EndOffset.append(str(key["EndOffset"]))
    #추출된 키워드의 점수,텍스트,문장의 시작위치,끝 위치
    pair = list(zip(score,text,BeginOffset,EndOffset)) #confidence에 따른 정렬

#    print(okt.normalize(result['value']))
#    print(text_input)

    #불용어 파일에 해당하는 불용어 키워드 제거
    #단어 전체가 완전히 불용어인 경우만 제거 ex 유강이랑 - 제거 x , 에서 - 제거 d
    D_pair = del_pair(pair)

    #불용어가 제거된 키워드에서 위치정보에 따라 조사제거 - 유강이랑 -> 유강,유강
    J_pair = josa_del(J_list,D_pair)

    #띄어쓰기 기준으로 단어 분할 , 이후 불용어 키워드 한번 더 제거
    re_pair = pair_replace(J_pair)


    """
    for Text in json_keyword['KeyPhrases']:
        keywords.append(Text['Text'])
    """
    #return keywords
    return re_pair


kakao_speech_url = "https://kakaoi-newtone-openapi.kakao.com/v1/recognize"

rest_api_key = 'a0b818404883532ce93da157ad839f89'

headers = {
    "Content-Type": "application/octet-stream",
    "X-DSS-Service": "DICTATION",
    "Authorization": "KakaoAK " + rest_api_key,
}


def del_pair(pair): # 불용어 제거
    pair_len = len(pair)
    delist = list()
    for i in range(0,pair_len):
            for k in stopword:
                if pair[i][1] == k:
                    delist.append(pair[i])
    try:
        for i in delist:
            pair.remove(i)
    except:
        return pair

    return pair


def pair_replace(pair): #스페이스바 기준으로 나눔
    del_pair(pair)
    k = list()
    for i in pair:
        if i[1].find(" ") >= 0 :
#             k.append((i[0],i[1].replace(" ",""),i[2],i[3]))
            for j in i[1].split():
                k.append((i[0],j,i[2],i[3]))
        else:
            k.append((i[0],i[1],i[2],i[3]))
    k = del_pair(k)
    k = list(set(k))
    k.sort(reverse=True)
    return k

#조사 위치정보 확인
def josa_list(text):
    text_input = text
    josa_list = list()
    search_len = 0
    for i in okt.pos(text_input):
        search_len =  search_len + text_input[search_len:].find(i[0]) + len(i[0])

        if i[1] == 'Josa':
            k = (i[0],i[1] , search_len-len(i[0]),search_len)
            josa_list.append(k)
    return josa_list

# 조사 위치에 따른 제거
def josa_del(josa_list,re_pair):
    for j in josa_list:
        for k in range(0,len(re_pair)) :
            i = re_pair[k]
            if int(i[2]) <= int(j[2]) and int(i[3]) >= int(j[3]) :
                re_pair[k] =  (i[0],i[1][:int(j[2])-int(i[2])] + i[1][int(j[3])-int(i[2]):],i[2],i[3])
    return re_pair



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



STT_string = string_to_keyword("무신사랑해")
print(STT_string)

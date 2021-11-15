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

    text_input = string
    J_list = josa_list(text_input) #조사 위치정보 확인
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

    #불용어 파일에 해당하는 불용어 키워드 제거
    #단어 전체가 완전히 불용어인 경우만 제거 ex 유강이랑 - 제거 x , 에서 - 제거 d
    D_pair = del_pair(pair)

    #불용어가 제거된 키워드에서 위치정보에 따라 조사제거 - 유강이랑 -> 유강,유강
    J_pair = josa_del(J_list,D_pair)

    #띄어쓰기 기준으로 단어 분할 , 이후 불용어 키워드 한번 더 제거
    re_pair = pair_replace(J_pair)


    keywords = []
    for keyword in re_pair:
        keywords.append(keyword[1])

    return keywords


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
    k = []
#    print(pair)
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


# 처음 처리해야되는 부분

#동의어 pretrain된 모델 로딩
#FastText_path = '../cc.ko.300.bin'
#model = FT.load_fasttext_format(FastText_path)

#불용어 파일 불러오기
stopword_path = './ko_stopword.txt'
stopword = list()
with open(stopword_path, 'r',encoding='UTF8' ) as file:
    line = None
    while line != '':
        line = file.readline()
        stopword.append(line.strip('\n'))


path = './speech_records/'
file_list = os.listdir(path)
#print(file_list)


"""
string = ''
Full_string = []
#print("GFGF")
for file in file_list:
    try:
        #print("BBB")
        with open(path+file, 'rb') as fp:
            audio = fp.read()
        res = requests.post(kakao_speech_url, headers=headers, data=audio)

        result_json_string = res.text[res.text.index('{"type":"finalResult"'):res.text.rindex('}')+1]
        result = json.loads(result_json_string)
        #print(result)
        print(result['value'])
        #print("AAA")
        STT_string = string_to_keyword(result['value'])  #아마 STT_string 결과가 list 일 것, 그렇다면 현재는 바로 Full_string에 이어서 붙여 쓰고, 나중에 Amazon_comprehend쓸 때는 스트링으로 처리해야할 가능성이 생김
        print(STT_string)
        print("GFGFG")
        string += ' '  + result['value']
        print(string)
        print("BVBV")
        #print("BBB")
        #Full_string = "/".join()   #만약에 스트링으로 처리해야 한다면
        #print("CCC")
        Full_string.append(STT_string)
 #       print(STT_string)
        print(type(STT_string))

        text_input = okt.normalize(result['value'])
        print("text_input")
        J_list = josa_list(text_input)
        #os.remove(path+file)
        #print("B@:@:@")
        #return STT_string
        #return Full_string

    except Exception as e:    # 모든 예외의 에러 메시지를 출력할 때는 Exception을 사용
        print(e)
        pass
            #return Full_string



print(Full_string)
tmp = sum(Full_string, [])
print(tmp)

"""

#Amazon comprehend API 활성화
#comprehend = boto3.client(service_name='comprehend', region_name='us-east-1')

zsl = Pororo(task="zero-topic", lang="ko")

#test = zsl(string, ["음식", "의류", "화장품", "술", "생활용품", "음료"])

#print(zsl("나가서 뜨끈한 국밥 한그릇하자",["식사","스포츠","의류"]))
#print(string)
#print(test)





#comprehend = boto3.client(service_name = 'comprehend', region_name = 'us-east-1')

text = "테스트 중입니다. 치킨이랑 맥주먹고싶다 아침에 눈을 뜨면 해가 쨍쨍 눈사람이 반짝반짝 작은 별"
#json_keyword = comprehend.detect_key_phrases(Text=text, LanguageCode='ko')

print(text)
#text_input = okt.normalize(text)
#print(text_input)

STT_string = string_to_keyword(text)
#print("ASD")
print("키워드")
print(STT_string)


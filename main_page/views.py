from django.shortcuts import render, get_object_or_404
from main_page.models import AD_LIST
import random
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
import json, requests
import wave
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings

from main_page.key import KAKAO_API_KEY

import os
from datetime import datetime
import boto3
from pororo import Pororo
import pandas as pd
from gensim.models import FastText as FT
import numpy as np
from konlpy.tag import Okt
import random
okt=Okt()



def index(request):
    print("index.view start!!!")
    stored_ad_url = AD_LIST.objects.all()
    length = to_list(stored_ad_url)

    keyword, Full_sentence = wav_to_kakao_api(KAKAO_API_KEY())
    print(Full_sentence)

#--------------------------------케이스 3 가지처리해야함-----------------------------


#---------------1. GET으로 받았을 때, 현재 get으로 선택된 영상 출력 및 이거와 관련된 연관 동영상 출력---------------
    if request.method == 'GET':
        ad_key = request.GET.get('ad_key')

        if ad_key == None:
            pass

        else:
            GET_ad_key = ad_key
            ad_key = "https://www.youtube.com/watch?v=" + ad_key
            GET_ad_keyword = [AD_LIST.objects.get(ad_url = ad_key).tag1]
            GET_ad_keyword.append(AD_LIST.objects.get(ad_url = ad_key).tag2)
            GET_ad_keyword.append(AD_LIST.objects.get(ad_url = ad_key).tag3)
            GET_ad_keyword.append(AD_LIST.objects.get(ad_url = ad_key).tag4)

            GET_ad_id =  AD_LIST.objects.get(ad_url = ad_key).id
            GET_ad_name = AD_LIST.objects.get(ad_url = ad_key).ad_name
            GET_ad_feedback_value = AD_LIST.objects.get(ad_url = ad_key).feedback_value
            GET_ad_url = ad_key.replace("/watch?v=","/embed/")

            str_split = GET_ad_url.split("/embed/")
            ad_thumnail = str_split[1]
            ad_thumnail = "http://img.youtube.com/vi/" + ad_thumnail + "/mqdefault.jpg"

            GET_ad_main_keyword = [AD_LIST.objects.get(ad_url = ad_key).main_key_word]

            tmp_similar_ad = AD_LIST.objects.filter(main_key_word=GET_ad_main_keyword[0]).order_by('-feedback_value')
            similar_ad = tmp_similar_ad.values()
            print("similar_ad")
            print(similar_ad)
            if similar_ad:
                for queryset_dict in similar_ad:
                    modi_link = queryset_dict['ad_url']
                    modi_link = modi_link.split("/watch?v=")[1]
                    ad_link = "http://img.youtube.com/vi/" + modi_link + "/mqdefault.jpg"
                    queryset_dict.update(tmp = modi_link)
                    queryset_dict.update(ad_url = ad_link)
                    if ad_link == ad_thumnail:
                        queryset_dict.update(ad_url = '')
                        queryset_dict.update(name = '')
                        queryset_dict.update(ad_name = '')
                        queryset_dict.update(feedback_value = '')
                        queryset_dict.update(tmp = '')

            else:
                print("keyword 선택 안됨")
                pass

            context = {'selected_url': GET_ad_key, 'selected_name' : GET_ad_name  , 'selected_id' : GET_ad_id, 'similar_ad_list' : similar_ad,
                       'selected_ad_id_feedback_value' : GET_ad_feedback_value, 'scored_list' : GET_ad_keyword}
            return render(request, "main_page/index.html", context)


#---------------2. 음성파일이 없을 때, 랜덤으로 영상 출력 및 특정 조건으로 연관 영상들을 옆에 띄우기---------------
    if keyword == 0: #저장된 음성파일이 없으면
        print("음성파일 없고 랜덤")
        url_list, url_list_id = watch_to_embed(stored_ad_url)
        url_list_len = len(url_list)

        random_pick = random.randint(0, url_list_len -1)
        random_ad = url_list[random_pick] #+"?autoplay=1&mute=1"

        random_ad_id = url_list_id[random_pick]
        random_ad_id_feedback_value = AD_LIST.objects.get(id = random_ad_id).feedback_value

        random_ad_keyword = [AD_LIST.objects.get(id = random_ad_id).tag1]
        random_ad_keyword.append(AD_LIST.objects.get(id = random_ad_id).tag2)
        random_ad_keyword.append(AD_LIST.objects.get(id = random_ad_id).tag3)
        random_ad_keyword.append(AD_LIST.objects.get(id = random_ad_id).tag4)

        random_ad_name = AD_LIST.objects.get(id = random_ad_id).ad_name

        str_split = random_ad.split("/embed/")
        ad_thumnail = str_split[1]
        random_ad_key = str_split[1]
        ad_thumnail = "http://img.youtube.com/vi/" + ad_thumnail + "/mqdefault.jpg"

        random_ad_main_keyword = [AD_LIST.objects.get(ad_url = random_ad).main_key_word]
        tmp_similar_ad = AD_LIST.objects.filter(main_key_word=random_ad_main_keyword[0]).order_by('-feedback_value')
        similar_ad = tmp_similar_ad.values()

        if similar_ad:
            for queryset_dict in similar_ad:
                modi_link = queryset_dict['ad_url']
                modi_link = modi_link.split("/watch?v=")[1]
                ad_link = "http://img.youtube.com/vi/" + modi_link + "/mqdefault.jpg"
                queryset_dict.update(tmp = modi_link)
                queryset_dict.update(ad_url = ad_link)
                if ad_link == ad_thumnail:
                    queryset_dict.update(ad_url = '')
                    queryset_dict.update(name = '')
                    queryset_dict.update(ad_name = '')
                    queryset_dict.update(feedback_value = '')
                    queryset_dict.update(tmp = '')

        else:
            print("keyword 선택 안됨")
            pass

        print("Test3")
        print(similar_ad)


        feedback_value, feedback_id = Check_Feedback_value(stored_ad_url)

        context = {'selected_url': random_ad_key, 'selected_name' : random_ad_name, 'selected_id' : random_ad_id, 'similar_ad_list' : similar_ad,
                   'selected_ad_id_feedback_value' : random_ad_id_feedback_value, 'scored_list' : random_ad_keyword}


        return render(request, "main_page/index.html", context)


#-------------3. 음성파일이 있을 때, 그거와 관련된 영상 출력 및 동일한 메인 태그에 대한 연관 영상 띄우기 ----------------
    else:     #음성파일이 있으면
        print("음성파일 있음")        #음성 파일이 있는데, 광고 DB에 전부 매칭되지 않는 음성인 경우 처리해주어야함. random_pick 과정을 함수화 해서, 위에도 쓰고, 여기도 쓰면 좋을듯
        pick, scored_list = selected_ad(keyword, stored_ad_url, length, Full_sentence)
        print("scored_list")
        print(type(scored_list))
        print(scored_list)

        picked_ad = AD_LIST.objects.get(id=pick)
        picked_ad_name = picked_ad.ad_name
        picked_ad_main_keyword = picked_ad.main_key_word
        picked_ad_url = picked_ad.ad_url
        str_split = picked_ad_url.split("/watch?v=")
        picked_ad_key = str_split[1]
        ad_thumnail = str_split[1]
        ad_thumnail = "http://img.youtube.com/vi/" + ad_thumnail + "/mqdefault.jpg"

        picked_ad_url = picked_ad.ad_url.replace("/watch?v=","/embed/")
        picked_ad_feedback_value = picked_ad.feedback_value

        tmp_similar_ad = AD_LIST.objects.filter(main_key_word=picked_ad_main_keyword).order_by('-feedback_value')
        similar_ad = tmp_similar_ad.values()

        if similar_ad:
            for queryset_dict in similar_ad:
                modi_link = queryset_dict['ad_url']
                modi_link = modi_link.split("/watch?v=")[1]
                ad_link = "http://img.youtube.com/vi/" + modi_link + "/mqdefault.jpg"
                queryset_dict.update(tmp = modi_link)
                queryset_dict.update(ad_url = ad_link)
                if ad_link == ad_thumnail:
                    queryset_dict.update(ad_url = '')
                    queryset_dict.update(name = '')
                    queryset_dict.update(ad_name = '')
                    queryset_dict.update(feedback_value = '')
                    queryset_dict.update(tmp = '')

        else:
            print("keyword 선택 안됨")
            pass


        if len(similar_ad) == 0:
             tmp_similar_ad = AD_LIST.objects.filter(main_key_word=scored_list).order_by('-feedback_value')   #scored_list가 리스트 형태로 변경되면 이 구문 자체를 엎어야할 가능성 생김.
             similar_ad = tmp_similar_ad.values()
             if similar_ad:
                 for queryset_dict in similar_ad:
                     modi_link = queryset_dict['ad_url']
                     modi_link = modi_link.split("/watch?v=")[1]
                     ad_link = "http://img.youtube.com/vi/" + modi_link + "/mqdefault.jpg"
                     queryset_dict.update(tmp = modi_link)
                     queryset_dict.update(ad_url = ad_link)
                     if ad_link == ad_thumnail:
                         queryset_dict.update(ad_url = '')
                         queryset_dict.update(ad_name = '')
                         queryset_dict.update(feedback_value = '')
                         queryset_dict.update(tmp = '')

             else:
                 print("keyword 선택 안됨")
                 print("scored_list로도 처리 안됨") #단순하게 키워드 하나 가지고 처리되는 케이스
                 pass


        context = {'selected_url': picked_ad_key, 'selected_name' : picked_ad_name,'selected_id' : pick, 'selected_ad_id_feedback_value' : picked_ad_feedback_value,
                   'similar_ad_list' : similar_ad, 'scored_list' : scored_list}

        return render(request, "main_page/index.html", context)



def to_list(stored_ad_url):
    length = 0
    for list in stored_ad_url:
        length += 1
    return length

def watch_to_embed(stored_ad_url):
    list_of_ad_url=[]
    list_of_ad_id =[]
    for list in stored_ad_url:
        list_of_ad_url.append(list.ad_url.replace("/watch?v=","/embed/"))
        list_of_ad_id.append(list.id)

    return list_of_ad_url, list_of_ad_id

def P_feedback(request):
#    if request.is_ajax():
#        random_pick = request.GET['P_key']
    if request.method=="GET":
        random_pick = request.GET.get('P_key', None)

    v =  AD_LIST.objects.get(id=random_pick)
    v.feedback_value +=1
    v.save()
    context = {'update_feedback_value' : v.feedback_value}
    return HttpResponse(json.dumps(context), content_type="application/json")


def N_feedback(request):
#    if request.is_ajax():
#        random_pick = request.GET['N_key']
    if request.method=="GET":
        random_pick = request.GET.get('N_key', None)

    v =  AD_LIST.objects.get(id=random_pick)
    v.feedback_value -=1
    v.save()
    context = {'update_feedback_value' : v.feedback_value}
    return HttpResponse(json.dumps(context), content_type="application/json")

def Check_Feedback_value(stored_ad_url):
    list_of_ad_feedback_value=[]
    list_of_ad_id =[]
    for list in stored_ad_url:
        list_of_ad_feedback_value.append(list.feedback_value)
        list_of_ad_id.append(list.id)
    return list_of_ad_feedback_value, list_of_ad_id

@csrf_exempt
def upload(request):
    audio_data = request.FILES['audio_data']
    now = datetime.now().strftime("%Y%m%d-%H%M%S")
    file_name = './speech_records/'+now+'.wav'
    audio = wave.open(file_name, 'wb')
    audio.setnchannels(1)
    audio.setnframes(1)
    audio.setsampwidth(2)
    audio.setframerate(16000)
    blob = audio_data.read()
    audio.writeframes(blob)
    return JsonResponse({})


def wav_to_kakao_api(rest_api_key):
    import requests
    import json
    kakao_speech_url = "https://kakaoi-newtone-openapi.kakao.com/v1/recognize"
    STT_string = []
    tmp_string = []
    Full_keyword = []
    path = './speech_records/'
    file_list = os.listdir(path)

    headers = {
        "Content-Type": "application/octet-stream",
        "X-DSS-Service": "DICTATION",
        "Authorization": "KakaoAK " + rest_api_key,
    }

    string = ''
    for file in file_list:
        try:
            with open(path+file, 'rb') as fp:
                audio = fp.read()
            res = requests.post(kakao_speech_url, headers=headers, data=audio)
            os.remove(path+file)
            result_json_string = res.text[res.text.index('{"type":"finalResult"'):res.text.rindex('}')+1]
            result = json.loads(result_json_string)
            STT_string = string_to_keyword(result['value'])  #아마 STT_string 결과가 list 일 것, 그렇다면 현재는 바로 Full_string에 이어서 붙여 쓰고, 나중에 Amazon_comprehend쓸 때는 스트링으로 처리해야할 가능성이 생김
            string += ' ' + result['value']
            tmp_string.append(STT_string)
        except:
            pass

    Full_keyword = sum(tmp_string, [])
    return Full_keyword, string

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


def del_pair(pair): # 불용어 제거

    #불용어 파일 불러오기
    stopword_path = './ko_stopword.txt'
    stopword = list()
    with open(stopword_path, 'r',encoding='UTF8' ) as file:
        line = None
        while line != '':
            line = file.readline()
            stopword.append(line.strip('\n'))

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
    print(pair)
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


def selected_ad(keyword, stored_ad_url, length, Full_sentence):         #태그매칭으로 직접 광고를 선택할 함수       #현재는 전수조사 형태로 pick 합시다.
#결국 결정된 ad의 id값만 따서 리턴해주면 됨.
    tmp_list = []
    tmp_tag_list = []
    tmp_id_list = []
    ad_keyword_cnt = [0 for i in range(length)]
    result = 0

    scored_list = []
    max_tag_cnt = -1
    tmp_tag_cnt = 0


    zsl = Pororo(task="zero-topic", lang="ko")
    sentence_main_keyword = zsl(Full_sentence, ["음식", "의류", "화장품", "술", "생활용품", "음료"])   #추후 이 지역은 변경해주어야 함.
    max = 0
    picked_main_keyword = []
    for key in sentence_main_keyword:
        if sentence_main_keyword[key] > max:
            max = sentence_main_keyword[key]
            picked_main_keyword = key

    print("PICKED")
    print(picked_main_keyword)

    """
    for i, list in enumerate(stored_ad_url):       #모든 ad_list에 대하여 진행
        tmp_id_list.append(list.id)
        tmp_list.append(list.main_key_word)
        tmp_list.append(list.tag1)
        tmp_list.append(list.tag2)
        tmp_list.append(list.tag3)
        tmp_list.append(list.tag4)
    """

    #main_keyword 중심으로 한 번 거르기 위해 main_keyword만 중복없이  추출함.
    for list in stored_ad_url:
        if list.main_key_word not in tmp_list:
            tmp_list.append(list.main_key_word)

    for keyword_in_list in keyword:
        if keyword_in_list in tmp_list:   #이 부분 날려야 함.
            #main_keywords_tag_list = AD_LIST.objects.filter(main_key_word=keyword_in_list).order_by('-feedback_value')
            main_keywords_tag_list = AD_LIST.objects.filter(main_key_word=picked_main_keyword).order_by('-feedback_value')
            main_keywords_tag_list = main_keywords_tag_list.values()
            for dict in main_keywords_tag_list:
                if dict['tag1'] in keyword:
                    tmp_tag_cnt = tmp_tag_cnt + 1
                if dict['tag2'] in keyword:
                    tmp_tag_cnt = tmp_tag_cnt + 1
                if dict['tag3'] in keyword:
                    tmp_tag_cnt = tmp_tag_cnt + 1
                if dict['tag4'] in keyword:
                    tmp_tag_cnt = tmp_tag_cnt + 1

                if max_tag_cnt < tmp_tag_cnt:
                    max_tag_cnt = tmp_tag_cnt
                    tmp_tag_cnt = 0
                    scored_list = []
                    scored_list.append(dict['tag1'])
                    scored_list.append(dict['tag2'])
                    scored_list.append(dict['tag3'])
                    scored_list.append(dict['tag4'])
                    result = dict['id']
        """
        for j in range(0,4):   #각각 4번 돌릴거
            if tmp_list[j] in keyword:
                ad_keyword_cnt[i] += 1
                #여기서는 각 ad_list 에 count + 1    제일 많이 카운트 된 순위로 결정, 동점자 발생 시, 가장 앞쪽  순서로 처리
                if tmp_list[j] not in scored_list:
                    scored_list.append(tmp_list[j])
        tmp_list = []
        """

    if len(scored_list) == 0:
        url_list, url_list_id = watch_to_embed(stored_ad_url)
        url_list_len = len(url_list)

        random_pick = random.randint(0, url_list_len -1)
        random_ad = url_list[random_pick]

        random_ad_id = url_list_id[random_pick]
        #random_ad_id_feedback_value = AD_LIST.objects.get(id = random_ad_id).feedback_value

        random_ad_keyword = []
        random_ad_keyword.append(AD_LIST.objects.get(id = random_ad_id).main_key_word)
        #random_ad_name = AD_LIST.objects.get(id = random_ad_id).ad_name

        return random_ad_id, random_ad_keyword


#    if max(ad_keyword_cnt) == 0:     #이 부분은 나중에 음성에서 뽑힌 키워드랑 광고랑전혀 매칭 안될 때, 처리하기위한 구문
#    else:
#        result = tmp_id_list[ad_keyword_cnt.index(max(ad_keyword_cnt))]

#    result = tmp_id_list[ad_keyword_cnt.index(max(ad_keyword_cnt))]
    print("result")
    print(result)

    print("scored_list")
    print(scored_list)

    return result, scored_list           #결정된 ad의 id값, 그 때 사용된 scored_list

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

import os, shutil
from datetime import datetime


def index(request):
    print("index.view start!!!")
    stored_ad_url = AD_LIST.objects.all()
    length = to_list(stored_ad_url)

    keyword = wav_to_kakao_api(KAKAO_API_KEY())
    print("keyword")
    print(keyword)
    print(type(keyword))

#--------------------------------케이스 3 가지처리해야함-----------------------------


#---------------1. GET으로 받았을 때, 현재 get으로 선택된 영상 출력 및 이거와 관련된 연관 동영상 출력---------------
    if request.method == 'GET':
        ad_key = request.GET.get('ad_key')

        if ad_key == None:
            pass

        else:
            GET_ad_key = ad_key
            ad_key = "https://www.youtube.com/watch?v=" + ad_key
            GET_ad_keyword = [AD_LIST.objects.get(ad_url = ad_key).main_key_word]
            GET_ad_id =  AD_LIST.objects.get(ad_url = ad_key).id
            GET_ad_name = AD_LIST.objects.get(ad_url = ad_key).ad_name
            GET_ad_feedback_value = AD_LIST.objects.get(ad_url = ad_key).feedback_value
            GET_ad_url = ad_key.replace("/watch?v=","/embed/")

            str_split = GET_ad_url.split("/embed/")
            ad_thumnail = str_split[1]
            ad_thumnail = "http://img.youtube.com/vi/" + ad_thumnail + "/mqdefault.jpg"

            tmp_similar_ad = AD_LIST.objects.filter(main_key_word=GET_ad_keyword[0]).order_by('-feedback_value')
            similar_ad = tmp_similar_ad.values()
            print("similar_ad")
            print(similar_ad)
            if similar_ad:
                for queryset_dict in similar_ad:
                    modi_link = queryset_dict['ad_url']
                    modi_link = modi_link.split("/watch?v=")[1]
                    ad_link = "http://img.youtube.com/vi/" + modi_link + "/mqdefault.jpg"
                    queryset_dict.update(tag3 = modi_link) #tag3를 임시로ad_key값을 위해  사용
                    queryset_dict.update(ad_url = ad_link)
                    if ad_link == ad_thumnail:
                        queryset_dict.update(ad_url = '')
                        queryset_dict.update(name = '')
                        queryset_dict.update(ad_name = '')
                        queryset_dict.update(feedback_value = '')
                        queryset_dict.update(tag3 = '')

            else:
                print("keyword 선택 안됨")
                pass

            context = {'selected_url': GET_ad_key, 'selected_name' : GET_ad_name  , 'selected_id' : GET_ad_id, 'similar_ad_list' : similar_ad,
                       'selected_ad_id_feedback_value' : GET_ad_feedback_value, 'scored_list' : GET_ad_keyword}
            return render(request, "main_page/index.html", context)


#---------------2. 음성파일이 없을 때, 랜덤으로 영상 출력 및 특정 조건으로 연관 영상들을 옆에 띄우기---------------
    if keyword == 0: #저장된 음성파일이 없으면
        url_list, url_list_id = watch_to_embed(stored_ad_url)
        url_list_len = len(url_list)

        random_pick = random.randint(0, url_list_len -1)
        random_ad = url_list[random_pick] #+"?autoplay=1&mute=1"

        random_ad_id = url_list_id[random_pick]
        random_ad_id_feedback_value = AD_LIST.objects.get(id = random_ad_id).feedback_value

        random_ad_keyword = [AD_LIST.objects.get(id = random_ad_id).main_key_word]
        random_ad_name = AD_LIST.objects.get(id = random_ad_id).ad_name

        str_split = random_ad.split("/embed/")
        ad_thumnail = str_split[1]
        random_ad_key = str_split[1]
        ad_thumnail = "http://img.youtube.com/vi/" + ad_thumnail + "/mqdefault.jpg"

        tmp_similar_ad = AD_LIST.objects.filter(main_key_word=random_ad_keyword[0]).order_by('-feedback_value')
        similar_ad = tmp_similar_ad.values()

        if similar_ad:
            for queryset_dict in similar_ad:
                modi_link = queryset_dict['ad_url']
                modi_link = modi_link.split("/watch?v=")[1]
                ad_link = "http://img.youtube.com/vi/" + modi_link + "/mqdefault.jpg"
                queryset_dict.update(tag3 = modi_link) #tag3를 임시로ad_key값을 위해  사용
                queryset_dict.update(ad_url = ad_link)
                if ad_link == ad_thumnail:
                    queryset_dict.update(ad_url = '')
                    queryset_dict.update(name = '')
                    queryset_dict.update(ad_name = '')
                    queryset_dict.update(feedback_value = '')
                    queryset_dict.update(tag3 = '')

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
        pick, scored_list = selected_ad(keyword, stored_ad_url, length)
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
                queryset_dict.update(tag3 = modi_link) #tag3를 임시로ad_key값을 위해  사용
                queryset_dict.update(ad_url = ad_link)
                if ad_link == ad_thumnail:
                    queryset_dict.update(ad_url = '')
                    queryset_dict.update(name = '')
                    queryset_dict.update(ad_name = '')
                    queryset_dict.update(feedback_value = '')
                    queryset_dict.update(tag3 = '')

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
                     queryset_dict.update(tag3 = modi_link) #tag3를 임시로ad_key값을 위해  사용
                     queryset_dict.update(ad_url = ad_link)
                     if ad_link == ad_thumnail:
                         queryset_dict.update(ad_url = '')
                         queryset_dict.update(ad_name = '')
                         queryset_dict.update(feedback_value = '')
                         queryset_dict.update(tag3 = '')

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
    file_name = now+'.wav'
    audio = wave.open(file_name, 'wb')
    audio.setnchannels(1)
    audio.setnframes(1)
    audio.setsampwidth(2)
    audio.setframerate(16000)
    blob = audio_data.read()
    audio.writeframes(blob)
    from_ = file_name
    to_ = './speech_records'
    shutil.move(from_, to_)
    return JsonResponse({})


def wav_to_kakao_api(rest_api_key):
    import requests
    import json
    kakao_speech_url = "https://kakaoi-newtone-openapi.kakao.com/v1/recognize"
    STT_string = []
    Full_string = []
    path = './speech_records/'
    file_list = os.listdir(path)

    headers = {
        "Content-Type": "application/octet-stream",
        "X-DSS-Service": "DICTATION",
        "Authorization": "KakaoAK " + rest_api_key,
    }
    print("EEEE")
    #이 부분에서 여러개의 .wav 파일을 카카오로 보낸 다음 결과로 받은 keyword 문장을 다 이어주어야 함.
    try:
        print("GFGF")
        for file in file_list:
            print("BBB")
            with open(path+file, 'rb') as fp:
                audio = fp.read()
            res = requests.post(kakao_speech_url, headers=headers, data=audio)

            result_json_string = res.text[res.text.index('{"type":"finalResult"'):res.text.rindex('}')+1]
            result = json.loads(result_json_string)
            print(result)
            print(result['value'])


            STT_string = string_to_keyword(result['value'])  #아마 STT_string 결과가 list 일 것, 그렇다면 현재는 바로 Full_string에 이어서 붙여 쓰고, 나중에 Amazon_comprehend쓸 때는 스트링으로 처리해야할 가능성이 생김
            #Full_string = "/".join()   #만약에 스트링으로 처리해야 한다면
            Full_string.append(STT_string)
            os.remove(path+file)
            print("B@:@:@")
            #return STT_string
        return Full_string

    except:
        return 0



def string_to_keyword(string):    #keyword로 쪼갤 아이디어 함수
    demo = string.split(' ')
    print(demo)                #이후에 보완해야함
    search = ['이','가','을','를',
              '에','에서','의','한테',
              '고','라고','처럼','만큼',
              '와','과','은','는','뿐',
              '만','요','란','다','랑','이다',
             ]
    for i, word in enumerate(demo):
        for j in range(len(search)):
            if search[j] in word:
                print('>> modify: ' + word)
                demo[i] = word.strip(search[j])
    print(demo)
    return demo


def selected_ad(keyword, stored_ad_url, length):         #태그매칭으로 직접 광고를 선택할 함수       #현재는 전수조사 형태로 pick 합시다.
#결국 결정된 ad의 id값만 따서 리턴해주면 됨.
    tmp_list = []
    tmp_id_list = []
    ad_keyword_cnt = [0 for i in range(length)]
    print(len(ad_keyword_cnt))
    result = 0

    scored_list = []

    for i, list in enumerate(stored_ad_url):       #모든 ad_list에 대하여 진행
        tmp_id_list.append(list.id)
        tmp_list.append(list.main_key_word)
        tmp_list.append(list.tag1)
        tmp_list.append(list.tag2)
        tmp_list.append(list.tag3)

        for j in range(0,4):   #각각 4번 돌릴거
            if tmp_list[j] in keyword:
                ad_keyword_cnt[i] += 1
                #여기서는 각 ad_list 에 count + 1    제일 많이 카운트 된 순위로 결정, 동점자 발생 시, 가장 앞쪽  순서로 처리
                if tmp_list[j] not in scored_list:
                    scored_list.append(tmp_list[j])
        tmp_list = []

    print(scored_list)



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

    result = tmp_id_list[ad_keyword_cnt.index(max(ad_keyword_cnt))]
    print("result")
    print(result)

    return result, scored_list           #결정된 ad의 id값, 그 때 사용된 scored_list

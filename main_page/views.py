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


def index(request):
    print("index.view start!!!")
#    print(settings.KAKAO_API_KEY)
#    print(type(settings.KAKAO_API_KEY))
    stored_ad_url = AD_LIST.objects.all()
    length = to_list(stored_ad_url)
#    print(stored_ad_url)

#    keyword = wav_to_kakao_api(settings.KAKAO_API_KEY)   #rest_api == SECRET_KEY
    keyword = wav_to_kakao_api(KAKAO_API_KEY())
    print(keyword)

#--------------------------------케이스 3 가지처리해야함-----------------------------


#---------------1. GET으로 받았을 때, 현재 get으로 선택된 영상 출력 및 이거와 관련된 연관 동영상 출력---------------
#    if request.method == 'GET':
#        ad_key = request.GET['ad_key']

#        if ad_key == False:
#            pass

#        else:
#            print("ad_key")
#            print(ad_key)
#            data = { 'stored_ad_url' : ad_key,
#                   }

#        return render(request, "main_page/index.html", data)
#        context = {'stored_ad_url':stored_ad_url, 'url_list': url_list, 'selected_url': random_ad, 'selected_id' : random_ad_id, 'len': length,
#                   'feedback_value': feedback_value, 'feedback_id': feedback_id, 'selected_ad_id_feedback_value' : random_ad_id_feedback_value}



#---------------2. 음성파일이 없을 때, 랜덤으로 영상 출력 및 특정 조건으로 연관 영상들을 옆에 띄우기---------------
    if keyword == 0: #저장된 음성파일이 없으면
        url_list, url_list_id = watch_to_embed(stored_ad_url)
        url_list_len = len(url_list)

        random_pick = random.randint(0, url_list_len -1)
        random_ad = url_list[random_pick] #+"?autoplay=1&mute=1"

        random_ad_id = url_list_id[random_pick]
        random_ad_id_feedback_value = AD_LIST.objects.get(id = random_ad_id).feedback_value

        feedback_value, feedback_id = Check_Feedback_value(stored_ad_url)

        context = {'stored_ad_url':stored_ad_url, 'url_list': url_list, 'selected_url': random_ad, 'selected_id' : random_ad_id, 'len': length,
                   'feedback_value': feedback_value, 'feedback_id': feedback_id, 'selected_ad_id_feedback_value' : random_ad_id_feedback_value}
        return render(request, "main_page/index.html", context)


#-------------3. 음성파일이 있을 때, 그거와 관련된 영상 출력 및 동일한 메인 태그에 대한 연관 영상 띄우기 ----------------
    else:     #음성파일이 있으면
        print("음성파일 있음")        #음성 파일이 있는데, 광고 DB에 전부 매칭되지 않는 음성인 경우 처리해주어야함. random_pick 과정을 함수화 해서, 위에도 쓰고, 여기도 쓰면 좋을듯
        pick, scored_list = selected_ad(keyword, stored_ad_url, length)
        print(keyword)

        picked_ad = AD_LIST.objects.get(id=pick)
        picked_ad_url = picked_ad.ad_url
        str_split = picked_ad_url.split("/watch?v=")
        ad_thumnail = str_split[1]
        print("FGHDF")
        print(str_split)
        print(ad_thumnail)
        ad_thumnail = "http://img.youtube.com/vi/" + ad_thumnail + "/mqdefault.jpg"


        picked_ad_url = picked_ad.ad_url.replace("/watch?v=","/embed/")
        print(picked_ad_url)
        picked_ad_feedback_value = picked_ad.feedback_value

        for tag in keyword:
            print(tag)
            tmp_similar_ad = AD_LIST.objects.filter(main_key_word=tag).order_by('-feedback_value')
            similar_ad = tmp_similar_ad.values()
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
                        queryset_dict.update(ad_name = '')
                        queryset_dict.update(feedback_value = '')
                        queryset_dict.update(tag3 = '')

            else:
                print("keyword 선택 안됨")
                pass

        context = {'selected_url': picked_ad_url, 'selected_id' : pick, 'selected_ad_id_feedback_value' : picked_ad_feedback_value,
                   'scored_list' : scored_list, 'similar_ad_list' : similar_ad}

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

def audio(request):
    return render(request, "main_page/audio.html")

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
    print(request.FILES['audio_data'])
    audio_data = request.FILES['audio_data']
    print(type(audio_data))
    print(audio_data.size)
    audio = wave.open('t2est.wav', 'wb')
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

    keyword = []

    headers = {
        "Content-Type": "application/octet-stream",
        "X-DSS-Service": "DICTATION",
        "Authorization": "KakaoAK " + rest_api_key,
    }
    try:
        with open('t2est.wav', 'rb') as fp:
            audio = fp.read()
        res = requests.post(kakao_speech_url, headers=headers, data=audio)

        result_json_string = res.text[res.text.index('{"type":"finalResult"'):res.text.rindex('}')+1]
        result = json.loads(result_json_string)
        print(result)
        print(result['value'])

        keyword = string_to_keyword(result['value'])
        return keyword

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
        tmp_list =[]


    print(scored_list)

#    if max(ad_keyword_cnt) == 0:     #이 부분은 나중에 음성에서 뽑힌 키워드랑 광고랑전혀 매칭 안될 때, 처리하기위한 구문
#        result = 0
#    else:
#        result = tmp_id_list[ad_keyword_cnt.index(max(ad_keyword_cnt))]

    result = tmp_id_list[ad_keyword_cnt.index(max(ad_keyword_cnt))]
    print("result")
    print(result)

    return result, scored_list           #결정된 ad의 id값, 그 때 사용된 scored_list

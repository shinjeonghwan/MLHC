from django.shortcuts import render, get_object_or_404
from main_page.models import AD_LIST
import random
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
import json, requests
import wave
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings


def index(request):
    print("index.view start!!!")
#    print(settings.KAKAO_API_KEY)
#    print(type(settings.KAKAO_API_KEY))
    stored_ad_url = AD_LIST.objects.all()
    length = to_list(stored_ad_url)
#    print(stored_ad_url)

    keyword = wav_to_kakao_api(settings.KAKAO_API_KEY)   #rest_api == SECRET_KEY
    print(keyword)

    if keyword == 0: #저장된 음성파일이 없으면
        url_list, url_list_id = watch_to_embed(stored_ad_url)
        url_list_len = len(url_list)

        random_pick = random.randint(0, url_list_len -1)
        random_ad = url_list[random_pick] #+"?autoplay=1&mute=1"

        random_ad_id = url_list_id[random_pick]
        random_ad_id_feedback_value = AD_LIST.objects.get(id = random_ad_id).feedback_value

        feedback_value, feedback_id = Check_Feedback_value(stored_ad_url)

        context = {'stored_ad_url':stored_ad_url, 'url_list': url_list, 'rand_url': random_ad, 'random_pick' : random_ad_id, 'len': length,
                   'feedback_value': feedback_value, 'feedback_id': feedback_id, 'random_ad_id_feedback_value' : random_ad_id_feedback_value}
        return render(request, "main_page/index.html", context)

    else:     #음성파일이 있으면
        print("음성파일 있음")
        #pick =selected_ad(keyword)여기에 태그 매칭 할 알고리즘 넣기
        print(keyword)

#   return render(request, "main_page/index.html", context)

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
    audio = wave.open('t1est.wav', 'wb')
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
        with open('t1est.wav', 'rb') as fp:
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
    print(demo)
    return 2






#def select_ad():         #태그매칭으로 직접 광고를 선택할 함수








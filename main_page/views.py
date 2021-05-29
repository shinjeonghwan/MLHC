from django.shortcuts import render, get_object_or_404
from main_page.models import AD_LIST
import random
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse
import json
import wave
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings



def index(request):
    print("index.view start!!!")
    print(type(settings.KAKAO_API_KEY))
    stored_ad_url = AD_LIST.objects.all()
    length = to_list(stored_ad_url)
#    print(stored_ad_url)

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


def audio_record(request):

    audio_test = 1

    context = {'audio_test' : audio_test}
    return render (request, "main_page/record.html", context)


@csrf_exempt
def upload(request):
    print(request.FILES['audio_data'])
    audio_data = request.FILES['audio_data']
    print(type(audio_data))
    print(audio_data.size)
    audio = wave.open('test.wav', 'wb')
    audio.setnchannels(1) #1
    audio.setnframes(1)   #1
    audio.setsampwidth(4) #2
    audio.setframerate(16000) #48000
    blob = audio_data.read()
    audio.writeframes(blob) #on playing 'test.wav' only noise can be heard5

#    audio2 = wave.open('t5est.wav', 'wb')
#    audio2.setnchannels(1) #1
#    audio2.setnframes(1)   #1
#    audio2.setsampwidth(4) #1
#    audio2.setframerate(000) #16000
#    audio2.writeframes(blob) #on playing 'test.wav' only noise can be heard

#    audio3 = wave.open('t6est.wav', 'wb')
#    audio3.setnchannels(1) #1
#    audio3.setnframes(1)   #1
#    audio3.setsampwidth(2) #1
#    audio3.setframerate(48000) #16000
#    audio3.writeframes(blob) #on playing 'test.wav' only noise can be heard

#    audio4 = wave.open('t7est.wav', 'wb')
#    audio4.setnchannels(1) #1
#    audio4.setnframes(1)   #1
#    audio4.setsampwidth(2) #1
#    audio4.setframerate(48000) #16000
#    audio4.writeframes(blob) #on playing 'test.wav' only noise can be heard


    return JsonResponse({})

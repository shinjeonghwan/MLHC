from django.shortcuts import render, get_object_or_404
from main_page.models import AD_LIST
import random
from django.http import HttpResponseRedirect
from django.urls import reverse

def index(request):
    print("index.view start!!!")
    stored_ad_url = AD_LIST.objects.all()
    length = to_list(stored_ad_url)

    url_list, url_list_id = watch_to_embed(stored_ad_url)
    url_list_len = len(url_list)

    random_pick = random.randint(0, url_list_len -1)
    random_ad = url_list[random_pick]+"?autoplay=1&mute=1"
    print(random_ad)
    random_ad_id = url_list_id[random_pick]

    feedback_value, feedback_id = Check_Feedback_value(stored_ad_url)

    context = {'stored_ad_url':stored_ad_url, 'url_list': url_list, 'rand_url': random_ad, 'random_pick' : random_ad_id, 'len': length,
               'feedback_value': feedback_value, 'feedback_id': feedback_id}

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
        #print(list_of_ad_url)
        #print(list_of_ad_id)
    return list_of_ad_url, list_of_ad_id

def audio(request):
    return render(request, "main_page/audio.html")

def P_feedback(request, random_pick):
    v =  AD_LIST.objects.get(id=random_pick)
    v.feedback_value +=1
    v.save()
    return HttpResponseRedirect(reverse('main_page:index'))

def N_feedback(request, random_pick):
    v =  AD_LIST.objects.get(id=random_pick)
    v.feedback_value -=1
    v.save()
    return HttpResponseRedirect(reverse('main_page:index'))

def Check_Feedback_value(stored_ad_url):
    list_of_ad_feedback_value=[]
    list_of_ad_id =[]
    for list in stored_ad_url:
        list_of_ad_feedback_value.append(list.feedback_value)
        list_of_ad_id.append(list.id)
    return list_of_ad_feedback_value, list_of_ad_id


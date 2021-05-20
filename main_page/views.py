from django.shortcuts import render
from main_page.models import AD_LIST
import random

def index(request):
    print("index.view start!!!")
    stored_ad_url = AD_LIST.objects.all()
    length = to_list(stored_ad_url)

    url_list = watch_to_embed(stored_ad_url)
    url_list_len = len(url_list)

    random_pick = random.randint(0, url_list_len -1)
    random_ad = url_list[random_pick]

    context = {'stored_ad_url':stored_ad_url, 'url_list': url_list, 'rand_url': random_ad, 'len': length}
    return render(request, "main_page/index.html", context)


def to_list(stored_ad_url):
    length = 0
    for list in stored_ad_url:
        length += 1
    return length

def watch_to_embed(stored_ad_url):
    list_of_ad_url=[]
    for list in stored_ad_url:
        list_of_ad_url.append(list.ad_url.replace("/watch?v=","/embed/"))
        #print(list_of_ad_url)

    return list_of_ad_url



def audio(request):
    return render(request, "main_page/audio.html")

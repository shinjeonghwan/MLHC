from django.urls import path
from main_page import views

app_name = 'main_page'

urlpatterns = [
    path('', views.index, name="index"),
    path('audio/', views.audio, name='audio'),
#    path('audio/record' , views.audio_record, name='record'),
    path('upload/', views.upload, name='upload'),
    #path('<int:question_id>/', views.detail, name='detail'),
    #path('<int:question_id>/results/', views.results, name='results'),
#    path('<int:random_pick>/P_feedback/', views.P_feedback, name='P_feedback'),
    path('P_feedback/', views.P_feedback, name='P_feedback'),
    path('N_feedback/', views.N_feedback, name='N_feedback'),
#    path('<int:random_pick>/N_feeback/', views.N_feedback, name='N_feedback'),
]


from django.urls import path, include
from . import views

urlpatterns = [
    path('covid-prediction', views.covid_prediction, name="covid-prediction"),
    path('chatbot', views.chatbot, name="chatbot"),
]

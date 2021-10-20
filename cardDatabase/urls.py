from django.conf import settings
from django.urls import path
from django.shortcuts import redirect

from . import views

urlpatterns = [
    path('', lambda req: redirect('/search/')),
    path('search/', views.search, name='cardDatabase-search'),
    path('card/<str:card_id>/', views.view_card, name='cardDatabase-view-card')
]
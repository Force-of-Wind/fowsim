from django.conf import settings
from django.urls import path

from . import views

urlpatterns = [
    path('search/', views.search, name='cardDatabase-search'),
    path('card/<str:card_id>/', views.view_card, name='cardDatabase-view-card')
]
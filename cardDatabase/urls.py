from django.conf import settings
from django.urls import path
from django.shortcuts import redirect

from . import views

urlpatterns = [
    path('', lambda req: redirect('/search/')),
    path('search/', views.search_for_cards, name='cardDatabase-search'),
    path('card/<str:card_id>/', views.view_card, name='cardDatabase-view-card'),
    path('add_card/', views.add_card, name='cardDatabase-add-card'),
    path('test_error/', views.test_error, name='cardDatabase-test-error'),
]
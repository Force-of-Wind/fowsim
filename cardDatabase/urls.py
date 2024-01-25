from django.contrib.auth import views as DjangoAuthViews
from django.urls import path
from django.shortcuts import redirect

from . import views
from .forms import UserLoginForm

urlpatterns = [
    path('', lambda req: redirect('/search/'), name='cardDatabase-home'),
    path('search/', views.search_for_cards, name='cardDatabase-search'),
    path('card/<str:card_id>/', views.view_card, name='cardDatabase-view-card'),
    path('add_card/', views.add_card, name='cardDatabase-add-card'),
    path('decklists/', views.deprecated_decklist_url, name='cardDatabase-user-decklists'),
    path('create_decklist/', views.create_decklist, name='cardDatabase-create-decklist'),
    path('edit_decklist/<int:decklist_id>/', views.edit_decklist, name='cardDatabase-edit-decklist'),
    path('edit_decklist_mobile/<int:decklist_id>/', views.edit_decklist_mobile, name='cardDatabase-edit-decklist-mobile'),
    path('save_decklist/<int:decklist_id>/', views.save_decklist, name='cardDatabase-save-decklist'),
    path('create_share_code/<int:decklist_id>/', views.create_share_code, name='cardDatabase-save-share-code'),
    path('delete_share_code/<int:decklist_id>/', views.delete_share_code, name='cardDatabase-delete-share-code'),
    path('deck/<int:decklist_id>/', lambda req, decklist_id=None: redirect('cardDatabase-view-decklist', decklist_id=decklist_id)),
    path('view_decklist/<int:decklist_id>/', views.view_decklist, name='cardDatabase-view-decklist'),
    path('view_decklist/<int:decklist_id>/<str:share_parameter>/', views.view_decklist, name='cardDatabase-view-decklist-share'),
    path('decklist/view/<str:username>', views.view_users_public, name='cardDatabase-view-users-decklist'),
    path('delete_decklist/<int:decklist_id>/', views.delete_decklist, name='cardDatabase-delete-decklist'),
    path('test_error/', views.test_error, name='cardDatabase-test-error'),
    path('logout/', views.logout, name='cardDatabase-logout'),
    path('preferences/', views.userPreferences, name='cardDatabase-user-preferences'),
    path('login/', DjangoAuthViews.LoginView.as_view(template_name='registration/login.html',
                                                     authentication_form=UserLoginForm), name='cardDatabase-login'),
    path('register/', views.register, name='cardDatabase-register'),
    path('desktop_only/', views.desktop_only, name='cardDatabase-desktop-only'),
    path('mobile_only/', views.mobile_only, name='cardDatabase-mobile-only'),
    path('copy_decklist/<int:decklist_id>/', views.copy_decklist, name='cardDatabase-copy-decklist'),
    path('private_decklist/', views.private_decklist, name='cardDatabase-private-decklist'),
    path('tournament_decklist/', views.tournament_decklist, name='cardDatabase-tournament-decklist'),
    path('reddit_bot/query/', views.reddit_bot_query, name='cardDatabase-reddit-bot-query'),
    path('metrics', views.metrics, name='cardDatabase-metrics'),
    path('pack_opening/<str:setcode>/', views.pack_opening, name='cardDatabase-pack-opening'),
    path('pack_select/', views.pack_select, name='cardDatabase-pack-select'),
    path('pack_history/', views.pack_history, name='cardDatabase-pack-history')
]
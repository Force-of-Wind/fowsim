from django.contrib.auth import views as DjangoAuthViews
from django.urls import path
from django.shortcuts import redirect

from . import views
from .tournament import tournament_views, tournament_api_views
from .forms import UserLoginForm
from .views import search, search_for_decklist, deprecated_decklist_url, create_decklist, edit_decklist, \
    edit_decklist_mobile, view_decklist, view_user_public, delete_decklist, logout, user_preferences, register, \
    desktop_only, mobile_only, copy_decklist, private_decklist, tournament_decklist, metrics, pack_opening, pack_select, \
    pack_history, export_decklist, view_card
from .views.admin import add_card, test_error
from .views.bot import reddit_bot
from .views.post import save_decklist, create_share_code, delete_share_code

urlpatterns = [
    path('', lambda req: redirect('/search/'), name='cardDatabase-home'),
    path('search/', search.get, name='cardDatabase-search'),
    path('decklist_search/', search_for_decklist.get, name='cardDatabase-decklist-search'),
    path('card/<str:card_id>/', view_card.get, name='cardDatabase-view-card'),
    path('add_card/', add_card.get, name='cardDatabase-add-card'),
    path('decklists/', deprecated_decklist_url.get, name='cardDatabase-user-decklists'),
    path('create_decklist/<str:format>/', create_decklist.get, name='cardDatabase-create-decklist'),
    path('edit_decklist/<int:decklist_id>/', edit_decklist.get, name='cardDatabase-edit-decklist'),
    path('edit_decklist_mobile/<int:decklist_id>/', edit_decklist_mobile.get, name='cardDatabase-edit-decklist-mobile'),
    path('save_decklist/<int:decklist_id>/', save_decklist.post, name='cardDatabase-save-decklist'),
    path('create_share_code/<int:decklist_id>/', create_share_code.post, name='cardDatabase-save-share-code'),
    path('delete_share_code/<int:decklist_id>/', delete_share_code.post, name='cardDatabase-delete-share-code'),
    path('deck/<int:decklist_id>/', lambda req, decklist_id=None: redirect('cardDatabase-view-decklist', decklist_id=decklist_id)),
    path('view_decklist/<int:decklist_id>/', view_decklist.get, name='cardDatabase-view-decklist'),
    path('view_decklist/<int:decklist_id>/<str:share_parameter>/', view_decklist.get, name='cardDatabase-view-decklist-share'),
    path('decklist/view/<str:username>', view_user_public.get, name='cardDatabase-view-users-decklist'),
    path('delete_decklist/<int:decklist_id>/', delete_decklist.get, name='cardDatabase-delete-decklist'),
    path('test_error/', test_error.get, name='cardDatabase-test-error'),
    path('logout/', logout.get, name='cardDatabase-logout'),
    path('preferences/', user_preferences.get, name='cardDatabase-user-preferences'),
    path('login/', DjangoAuthViews.LoginView.as_view(template_name='registration/login.html',
                                                     authentication_form=UserLoginForm), name='cardDatabase-login'),
    path('register/', register.get, name='cardDatabase-register'),
    path('desktop_only/', desktop_only.get, name='cardDatabase-desktop-only'),
    path('mobile_only/', mobile_only.get, name='cardDatabase-mobile-only'),
    path('copy_decklist/<int:decklist_id>/', copy_decklist.get, name='cardDatabase-copy-decklist'),
    path('private_decklist/', private_decklist.get, name='cardDatabase-private-decklist'),
    path('locked_decklist/', locked_decklist.get, name='cardDatabase-locked-decklist'),
    path('reddit_bot/query/', reddit_bot.get, name='cardDatabase-reddit-bot-query'),
    path('metrics', metrics.get, name='cardDatabase-metrics'),
    path('pack_opening/<str:setcode>/', pack_opening.get, name='cardDatabase-pack-opening'),
    path('pack_select/', pack_select.get, name='cardDatabase-pack-select'),
    path('pack_history/', pack_history.get, name='cardDatabase-pack-history'),
    path('api/deck/<int:decklist_id>/', export_decklist.get, name='cardDatabase-export-decklist'),

    # TOURNAMENT SECTION
    path('tournaments/', tournament_views.show_tournaments, name='cardDatabase-tournament-list'),
    path('new_tournament/', tournament_views.new_tournament, name='cardDatabase-new-tournament'),
    path('create_tournament/', tournament_views.create_tournament, name='cardDatabase-create-tournament'),
    path('edit_tournament/<int:tournament_id>/', tournament_views.edit_tournament, name='cardDatabase-edit-tournament'),
    path('tournament_delete/<int:tournament_id>/', tournament_views.delete_tournament, name='cardDatabase-delete-tournament'),
    path('tournament_detail/<int:tournament_id>/', tournament_views.tournament_detail, name='cardDatabase-detail-tournament'),
    path('tournament_admin/<int:tournament_id>/', tournament_views.tournament_admin, name='cardDatabase-admin-tournament'),


    #TOURNAMENT API
    path('api/tournament/<int:tournament_id>/phase/update/', tournament_api_views.update_tournament_phase, name='cardDatabase-update-tournament-phase'),
    path('api/tournament/<int:tournament_id>/players/', tournament_api_views.get_tournament_players, name='cardDatabase-get-tournament-players'),
    path('api/tournament/<int:tournament_id>/players/update/', tournament_api_views.update_tournament_players, name='cardDatabase-save-tournament-players'),
    #path('tournament_admin/<int:tournament_id>/', tournament_api_views.tournament_admin, name='cardDatabase-admin-tournament'),
]
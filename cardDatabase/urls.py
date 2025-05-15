from django.contrib.auth import views as DjangoAuthViews
from django.urls import path
from django.shortcuts import redirect

from .forms import UserLoginForm
from .views import search, search_for_decklist, deprecated_decklist_url, create_decklist, edit_decklist, \
    edit_decklist_mobile, view_decklist, view_user_public, delete_decklist, logout, user_preferences, register, \
    desktop_only, mobile_only, copy_decklist, private_decklist, locked_decklist, metrics, pack_opening, pack_select, \
    pack_history, export_decklist, export_decklist_share, view_card
from .views.admin import add_card, test_error
from .views.bot import reddit_bot
from .views.post import save_decklist, create_share_code, delete_share_code, create_deck_lock, delete_deck_lock

from .views.tournament import delete_tournament, show_tournaments, new_tournament, edit_tournament, \
    tournament_detail, tournament_decklist, delete_tournament_registration, tournament_remove_invalid, \
    tournament_create_unauthorized
from .views.tournament.post import create_tournament, update_tournament
from .views.tournament.player import tournament_player_register, tournament_player_change_decklist
from .views.tournament.admin import get_tournament_players, tournament_admin
from .views.tournament.admin.post import decklist_reveal_status, remove_tournament_player, reset_phase, \
    lock_deck_edit, update_tournament_phase, update_tournament_players

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
    path('create_deck_lock/<int:decklist_id>/', create_deck_lock.post, name='cardDatabase-user-lock-decklist'),
    path('delete_deck_lock/<int:decklist_id>/', delete_deck_lock.post, name='cardDatabase-user-unlock-decklist'),
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
    path('api/deck/<int:decklist_id>/<str:share_parameter>', export_decklist_share.get, name='cardDatabase-export-decklist-share'),

    # TOURNAMENT
    path('tournaments/', show_tournaments.get, name='cardDatabase-tournament-list'),
    path('tournament/new/', new_tournament.get, name='cardDatabase-new-tournament'),
    path('tournament/<int:tournament_id>/edit/', edit_tournament.get, name='cardDatabase-edit-tournament'),
    path('tournament/<int:tournament_id>/detail/', tournament_detail.get, name='cardDatabase-detail-tournament'),
    path('tournament/<int:tournament_id>/admin/', tournament_admin.get, name='cardDatabase-admin-tournament'),
    path('tournament/<int:tournament_id>/player/registration/', tournament_player_register.get, name='cardDatabase-player-register-tournament'),
    path('tournament_decklist/', tournament_decklist.get, name='cardDatabase-tournament-decklist'),
    path('tournament_remove_invalid/', tournament_remove_invalid.get, name='cardDatabase-tournament-remove-invalid'),
    path('tournament_delete/<int:tournament_id>/', delete_tournament.get, name='cardDatabase-delete-tournament'),
    path('api/tournament/<int:tournament_id>/players/', get_tournament_players.get, name='cardDatabase-get-tournament-players'),
    path('tournament/<int:tournament_id>/delete/registration', delete_tournament_registration.get, name='cardDatabase-tournament-delete-registration'),
    path('tournament/<int:tournament_id>/deck/change', tournament_player_change_decklist.get, name='cardDatabase-tournament-change-decklist'),
    path('tournament/create/unauthorized', tournament_create_unauthorized.get, name='cardDatabase-tournament-create-unauthorized'),

    # TOURNAMENT POST
    path('create_tournament/', create_tournament.post, name='cardDatabase-create-tournament'),
    path('api/update_tournament/<int:tournament_id>/', update_tournament.post, name='cardDatabase-update-tournament'),
    path('api/tournament_player_register/<int:tournament_id>/', tournament_player_register.post, name='cardDatabase-register-player-to-tournament'),
    path('api/tournament/<int:tournament_id>/phase/update/', update_tournament_phase.post, name='cardDatabase-update-tournament-phase'),
    path('api/tournament/<int:tournament_id>/players/update/', update_tournament_players.post, name='cardDatabase-save-tournament-players'),
    path('api/tournament/<int:tournament_id>/decklist/reveal/update/', decklist_reveal_status.post, name='cardDatabase-update-tournament-decklist-reveal-status'),
    path('api/tournament/<int:tournament_id>/reset/phase', reset_phase.post, name='cardDatabase-update-tournament-reset-phase'),
    path('api/tournament/<int:tournament_id>/lock/deck-edit', lock_deck_edit.post, name='cardDatabase-update-tournament-lock-deck-edit'),
    path('api/tournament/<int:tournament_id>/players/remove/<int:player_id>/', remove_tournament_player.post, name='cardDatabase-remove-tournament-player'),
    path('api/tournament/<int:tournament_id>/deck/change', tournament_player_change_decklist.post, name='cardDatabase-tournament-change-player-decklist'),
]
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from backend import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="homepage"),
    path("welcome/", views.welcome_page, name="welcome"),
    path("points/", views.points, name="points"),
    path("points/", views.points, name="points"),
    path("points/<int:id>/", views.matchdayPoints, name="matchdayPoints"),
    path("transferFirst/", views.transferFirst, name="transferFirst"),
    path("register/", views.register, name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("addfootballerFirst/", views.footballerAddFirst, name="addFootballer"),
    path("noMatchday/", views.noCurrentMatchdays, name="noMatchdays"),
    path("admindashboard/", views.adminControlDashboard, name="adminDashboard"),
    path("createMatch/", views.createMatch, name="createMatch"),
    path("matchManage/<int:id>/", views.matchManage, name="matchManage"),
    path("addMatchEvent", views.addMatchEvent, name="addMatchEvent"),
    path("send_fr/<int:userID>", views.send_fr, name="send_fr"),
    path("accept_fr/<int:requestID>", views.accept_fr, name="accept_fr"),
    path("manageFr/", views.manageFr, name="manageFr"),
    path("transfer/", views.transfer, name="transfer"),
    path(
        "transferFootballer/<int:id>",
        views.transferFootballer,
        name="transferFootballer",
    ),
    path("makeTransfer/", views.makeTransfer, name="makeTransfer"),
    path("makeSubs/", views.substitutions, name="makeSubs"),
    path("subView/<int:id>", views.subView, name="subView"),
    path("subOnOff", views.subOnOff, name="subOnOff"),
    path("deletebonus/", views.bonus_delete, name="bonusDelete"),
    path("addbonus", views.bonus_create, name="addbonus"),
    path("setCaptain/", views.set_captain, name="setCaptain"),
    path("addHome/", views.add_starting_home, name="addHome"),
    path("addAway/", views.add_starting_away, name="addAway"),
    path("ranking/", views.rankingView, name="ranking"),
    path("deleteFriend/", views.remove_friend, name="deleteFriend"),
    path("deleteMatch/", views.delete_match, name="deleteMatch"),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

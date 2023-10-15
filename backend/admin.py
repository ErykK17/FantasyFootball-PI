from django.contrib import admin
from .models import *

admin.site.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'logo',
    ]

admin.site.register(Matchday)
class MatchdayAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'start_date',
        'end_date'
    ]

admin.site.register(Footballer)
class FootballerAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'team',
        'position',
        'points',
        'price',
    ]

admin.site.register(MyFootballer)
class MyFootballerAdmin(admin.ModelAdmin):
    list_display = [
        'footballer',
        'squad',
        'squad_role',
    ]

admin.site.register(User)
class UserAdmin(admin.ModelAdmin):  # noqa: D101

    list_display = [
        'username',
        'email',
    ]

admin.site.register(MatchEvent)
class MatchEventAdmin(admin.ModelAdmin):

    list_display = [
        'event_name',
        'points_granted',
    ]

admin.site.register(Match)
class MatchAdmin(admin.ModelAdmin):
    
    list_display = [
        'Matchday',
        'HomeTeam',
        'AwayTeam',
        'event',
    ]

admin.site.register(FootballersAction)
class FootballersActionAdmin(admin.ModelAdmin):

    list_display = [
        'event',
        'footballer',
    ]

admin.site.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = [
        'player_out',
        'player_in',
        'matchday',
        'owner',
    ]

admin.site.register(PowerUp)
class PowerUpAdmin(admin.ModelAdmin):
    list_display = [
        'owner',
        'is_used',
        'powerup_type',
        'matchday,'
    ]

admin.site.register(RankingScore)
class RankingScoreAdmin(admin.ModelAdmin):
    list_display = [
        'owner',
        'score'
    ]
admin.site.register(MatchdayScore)
class RankingScoreAdmin(admin.ModelAdmin):
    list_display = [
        'owner',
        'matchday',
        'score',
    ]

admin.site.register(FriendsRequest)
class FriendsRequest(admin.ModelAdmin):
    list_display = [
        'inviting_user',
        'recieving_user',
    ]
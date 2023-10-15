from django.db import models
from django.contrib.auth.models import AbstractUser
from django_countries.fields import CountryField 

class User(AbstractUser):
    friends = models.ManyToManyField("User", blank=True)

class FriendsRequest(models.Model):
    inviting_user = models.ForeignKey(User, related_name="inviting", on_delete=models.CASCADE)
    recieving_user = models.ForeignKey(User, related_name="recieving", on_delete=models.CASCADE)

class Team(models.Model):
    name = models.CharField(max_length=30)
    logo = models.ImageField('logo',blank=True, default='/media/ball.jpg')
    def __str__(self):
        return self.name

class Matchday(models.Model):
    name = models.CharField(max_length=30, default="MatchdayX")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    same_team_max = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.name

class Footballer(models.Model):
    name = models.CharField(max_length=30)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name="footballers")
    POSTION_CHOICES = (
        ("GK", "Bramkarz"),
        ("DF", "Obrońca"),
        ("MF", "Pomocnik"),
        ("FW", "Napastnik"))
    position = models.CharField(
            max_length=30,
            choices=POSTION_CHOICES,
            null=True)
    price = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class MyFootballer(models.Model):
    footballer = models.ForeignKey(Footballer, on_delete=models.CASCADE, null=True)
    SQUAD_ROLE_CHOICES = (
        ("FS", "Pierwszy skład"),
        ("SUBB", "Rezerwowy bramkarz"),
        ("SUB1", "Pierwszy rezerwowy"),
        ("SUB2", "Drugi rezerwowy"),
        ("SUB3", "Trzeci rezerwowy"))
    squad_role = models.CharField(max_length=30, choices=SQUAD_ROLE_CHOICES, null=True)
    owner = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )
    matchday = models.ForeignKey(Matchday, on_delete=models.CASCADE, null=True)
    points = models.IntegerField(default=0)
    captain = models.BooleanField(default=False)
    vice_captain = models.BooleanField(default=False)
    def __str__(self): 
        return self.footballer.name

class PowerUp(models.Model):
    owner = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    matchday = models.ForeignKey(
        Matchday,
        on_delete=models.CASCADE,
        null=True
    )
    is_used = models.BooleanField(default=False, null=True)
    
    POWERUP_CHOICES = (
        ("TC", "Potrójny kapitan"),
        ("SC", "Super Rezerwowi")
    )

    powerup_type = models.CharField(max_length=30, choices=POWERUP_CHOICES,null=True)

class MatchEvent(models.Model):
    event_name = models.CharField(max_length=30, null=True)
    points_granted = models.IntegerField(default=0, null=True)

    def __str__(self):
        return self.event_name

class FootballersAction(models.Model):
    event = models.ForeignKey(MatchEvent, on_delete=models.CASCADE, null=True)
    footballer = models.ForeignKey(Footballer, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.footballer.name} {self.event.event_name}'

class Match(models.Model):
    Matchday = models.ForeignKey(Matchday, on_delete=models.CASCADE, null=True)
    HomeTeam = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, related_name='home')
    AwayTeam = models.ForeignKey(Team, on_delete=models.CASCADE, null=True, related_name='away')
    HomePlayed = models.ManyToManyField(Footballer, blank=True, related_name='homeplayed')
    AvayPlayed = models.ManyToManyField(Footballer, blank=True, related_name='awayplayed')
    HomeGoals = models.IntegerField(default=0, null=True)
    AwayGoals = models.IntegerField(default=0, null=True)
    event = models.ManyToManyField(FootballersAction, blank=True)
    def __str__(self):
        return f'{self.HomeTeam.name} VS {self.AwayTeam.name}'

class Transfer(models.Model):
    player_out = models.ForeignKey(Footballer, on_delete=models.CASCADE, null=True, blank=True, related_name="player_out")
    player_in = models.ForeignKey(Footballer, on_delete=models.CASCADE, null=True, blank=True, related_name="player_in")
    matchday = models.ForeignKey(Matchday, on_delete=models.CASCADE, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE,null=True, blank=True)

class MatchdayScore(models.Model):
    owner = models.ForeignKey(User, blank=True,null=True, on_delete=models.CASCADE)
    matchday = models.ForeignKey(Matchday, blank=True, null=True, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)

class RankingScore(models.Model):
    owner = models.ForeignKey(User, blank=True,null=True, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
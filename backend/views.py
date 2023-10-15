from django.shortcuts import render, redirect, resolve_url
from .models import *
from .forms import CreateUserForm
from FantasyFootball.settings import LOGIN_REDIRECT_URL
from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
import datetime as d
from django.contrib.auth.decorators import login_required
from itertools import chain
from django.contrib.auth import authenticate, login


def register(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.save()
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
            )
            login(request, user)
            return HttpResponseRedirect("/welcome/")
    context = {"form": form}
    return render(request, "register.html", context)


class LoginView(LoginView):
    template_name = "login.html"

    def get_default_redirect_url(self):
        return resolve_url(LOGIN_REDIRECT_URL)


class LogoutView(LogoutView):
    template = "logout.html"


def reorganize(user, matchdayID):
    squad = MyFootballer.objects.filter(owner=user, matchday_id=matchdayID)
    matches = Match.objects.filter(Matchday_id=matchdayID)
    if matches.exists():
        for footballer in squad:
            for match in matches:
                if (
                    footballer.footballer not in match.AvayPlayed.all()
                    and footballer.footballer not in match.HomePlayed.all()
                ):
                    if footballer.squad_role == "FS":
                        sub_keeper = MyFootballer.objects.get(
                            squad_role="SUBB", matchday_id=matchdayID
                        )
                        if footballer.footballer.position == "GK" and (
                            sub_keeper.footballer in match.HomePlayed.all()
                            or sub_keeper.footballer in match.AvayPlayed.all()
                        ):
                            footballer.squad_role = None
                            footballer.save()
                            sub_keeper.squad_role = "FS"
                            sub_keeper.save()
                            footballer.squad_role = "SUB1"
                            footballer.save()
                        elif footballer.footballer.position != "GK":
                            first = MyFootballer.objects.get(
                                squad_role="SUB1", matchday_id=matchdayID
                            )
                            second = MyFootballer.objects.get(
                                squad_role="SUB2", matchday_id=matchdayID
                            )
                            third = MyFootballer.objects.get(
                                squad_role="SUB3", matchday_id=matchdayID
                            )
                            if (
                                (
                                    first.footballer in match.AvayPlayed.all()
                                    or first.footballer in match.HomePlayed.all()
                                )
                                and first.footballer.position
                                == footballer.footballer.position
                            ):
                                footballer.squad_role = None
                                footballer.save()
                                first.squad_role = "FS"
                                first.save()
                                footballer.squad_role = "SUB1"
                                footballer.save()
                            if (
                                (
                                    second.footballer in match.AvayPlayed.all()
                                    or second.footballer in match.HomePlayed.all()
                                )
                                and second.footballer.position
                                == footballer.footballer.position
                            ):
                                footballer.squad_role = None
                                footballer.save()
                                second.squad_role = "FS"
                                second.save()
                                footballer.squad_role = "SUB2"
                                footballer.save()
                            if (
                                (
                                    third.footballer in match.AvayPlayed.all()
                                    or third.footballer in match.HomePlayed.all()
                                )
                                and third.footballer.position
                                == footballer.footballer.position
                            ):
                                footballer.squad_role = None
                                footballer.save()
                                third.squad_role = "FS"
                                third.save()
                                footballer.squad_role = "SUB3"
                                footballer.save()


def calculate_points(myfootballer, matchday):
    score = 0
    footballer = myfootballer.footballer
    matchday = matchday
    matches = Match.objects.filter(Matchday=matchday)
    for match in matches:
        event = match.event.all()
        for event in event:
            if event.footballer == footballer:
                if myfootballer.captain and (
                    footballer in match.HomePlayed.all()
                    or footballer in match.AvayPlayed.all()
                ):
                    score += (event.event.points_granted) * 2
                elif myfootballer.vice_captain:
                    score += (event.event.points_granted) * 2
                else:
                    score += event.event.points_granted
    myfootballer.points = score
    myfootballer.save()


def calculate_matchday(user, matchdayID):
    reorganize(user, matchdayID)
    score = 0
    matchday = Matchday.objects.get(id=matchdayID)
    matches = Match.objects.filter(Matchday=matchdayID)
    myfootballers = MyFootballer.objects.filter(owner=user, matchday=matchdayID)
    matchday_score = MatchdayScore.objects.filter(owner=user, matchday=matchdayID)
    bonus = PowerUp.objects.filter(owner=user, matchday=matchdayID, powerup_type="SC")
    for mf in myfootballers:
        calculate_points(mf, matchdayID)
        if bonus.exists() and (
            mf.squad_role == "SUBB"
            or mf.squad_role == "SUB1"
            or mf.squad_role == "SUB2"
            or mf.squad_role == "SUB3"
        ):
            score += mf.points
        if mf.squad_role == "FS":
            score += mf.points
        if matchday_score.exists():
            update = MatchdayScore.objects.get(owner=user, matchday_id=matchdayID)
            update.score = score
            update.save()
        else:
            update = MatchdayScore.objects.create(
                owner=user, matchday_id=matchdayID, score=score
            )


def calculate_total(user):
    matchdays = Matchday.objects.all()
    ranking_score = RankingScore.objects.filter(owner=user)
    score = 0
    for matchday in matchdays:
        if MatchdayScore.objects.filter(owner=user, matchday_id=matchday.id).exists():
            calculate_matchday(user, matchday.id)
            score += MatchdayScore.objects.get(
                owner=user, matchday_id=matchday.id
            ).score
    if ranking_score.exists():
        ranking_score = RankingScore.objects.get(owner=user)
        ranking_score.score = score
        ranking_score.save()
    else:
        ranking_score = RankingScore.objects.create(owner=user, score=score)


@login_required
def rankingView(request, template_name="ranking.html"):
    users = User.objects.all()
    for user in users:
        calculate_total(user)
    scores = RankingScore.objects.all()
    user_score = RankingScore.objects.get(owner_id=request.user.id)
    scores_sorted = scores.order_by("-score")
    context = {"scores": scores_sorted}
    return render(request, template_name, context)


def home(response):
    return render(response, "base.html")


def noCurrentMatchdays(response):
    return render(response, "nomatchday.html")


@login_required
def send_fr(request, userID):
    inviting_user = request.user
    recieving_user = User.objects.get(id=userID)
    friend_request, created = FriendsRequest.objects.get_or_create(
        inviting_user=inviting_user, recieving_user=recieving_user
    )
    if created:
        return redirect("manageFr")
    return HttpResponse("Zaproszenie juz wysłane")


@login_required
def accept_fr(request, requestID):
    fr = FriendsRequest.objects.get(id=requestID)
    if fr.recieving_user == request.user:
        fr.recieving_user.friends.add(fr.inviting_user)
        fr.inviting_user.friends.add(fr.recieving_user)
        fr.delete()
        return redirect("manageFr")
    return HttpResponse("Zaproszenie nie zostało zaakceptowane")


@login_required
def manageFr(request, template_name="friends.html"):
    all_users = User.objects.all()
    all_fr = FriendsRequest.objects.filter(recieving_user=request.user)
    is_sent = FriendsRequest.objects.filter(inviting_user=request.user)
    sent_users = []
    for user in is_sent:
        sent_users.append(user.recieving_user)
    context = {"AllFr": all_fr, "AllUsers": all_users, "IsSent": sent_users}
    return render(request, template_name, context)


@login_required
def remove_friend(request):
    friend_to_remove = request.POST.get("friendID")
    friend = User.objects.get(id=friend_to_remove)
    user = User.objects.get(id=request.user.id)
    user.friends.remove(friend)
    return redirect("manageFr")


def calculate_squad_value(myfootballers):
    value = 0
    footballers = Footballer.objects.all()
    myfootballers_ids = []
    for mfootballer in myfootballers:
        myfootballers_ids.append(mfootballer.footballer.id)
    for footballer in footballers:
        if footballer.id in myfootballers_ids:
            value += footballer.price
    return value


def isMatchdayFinished(matchday):
    current_day = d.datetime.now().timestamp()
    if matchday.end_date.timestamp() < current_day:
        return True
    return False


def isMatchdayStarted(matchday):
    current_day = d.datetime.now().timestamp()
    if matchday.start_date.timestamp() <= current_day:
        return True
    return False


@login_required
def welcome_page(request):
    myfootballers = MyFootballer.objects.filter(owner=request.user)
    matchdays = Matchday.objects.all()
    active_matchdays = 0
    for mday in matchdays:
        if mday.start_date.timestamp() > d.datetime.now().timestamp():
            active_matchdays += 1
    if myfootballers.count() >= (15 * active_matchdays):
        have_played = True
    else:
        have_played = False
    context = {"HavePlayed": have_played}
    return render(request, "welcome.html", context)


@login_required
def points(request, template_name="points.html"):
    finished_matchdays = []
    matchdays = Matchday.objects.all()
    for mday in matchdays:
        if isMatchdayFinished(mday):
            finished_matchdays.append(mday)
    active_matchdays = 0
    for mday in matchdays:
        if mday.start_date.timestamp() > d.datetime.now().timestamp():
            active_matchdays += 1

    myfootballers = MyFootballer.objects.filter(owner=request.user)

    if myfootballers.count() >= (15 * active_matchdays):
        have_played = True
    else:
        have_played = False
    context = {"Matchdays": finished_matchdays, "HavePlayed": have_played}
    return render(request, template_name, context)


@login_required
def matchdayPoints(request, id, template_name="matchdaypoints.html"):
    finished_matchdays = []
    matchdays = Matchday.objects.all()
    for mday in matchdays:
        if isMatchdayFinished(mday):
            finished_matchdays.append(mday)
    current_matchday = Matchday.objects.get(id=id)
    if MyFootballer.objects.filter(owner=request.user).exists():
        myfootballers = MyFootballer.objects.filter(matchday=id, owner=request.user)
    else:
        myfootballers = None
    for footballer in myfootballers:
        calculate_points(footballer, current_matchday)
    calculate_matchday(request.user, current_matchday.id)
    score = 0
    if MatchdayScore.objects.filter(owner=request.user, matchday=current_matchday.id):
        score = MatchdayScore.objects.get(
            owner=request.user, matchday=current_matchday.id
        ).score
    context = {
        "MyFootballer": myfootballers,
        "current_matchday": current_matchday,
        "Matchdays": finished_matchdays,
        "Score": score,
    }
    return render(request, template_name, context)


@login_required
def transferFirst(request, template_name="transfersfirst.html"):
    if request.GET.get("position"):
        filter = request.GET.get("position")
        footballers = Footballer.objects.filter(position=filter).all()
        footballers = Footballer.objects.filter(position=filter).all()
    else:
        footballers = Footballer.objects.all()
    matchdays = Matchday.objects.all()

    transfer_matchday = None

    for mday in matchdays:
        if (not isMatchdayFinished(mday)) and (not isMatchdayStarted(mday)):
            transfer_matchday = mday
            break
    if transfer_matchday == None:
        return redirect("noMatchdays")

    if MyFootballer.objects.filter(owner=request.user).exists():
        myfootballers = MyFootballer.objects.filter(
            matchday=transfer_matchday.id, owner=request.user
        )
    else:
        myfootballers = None

    if myfootballers:
        budget = 150000000 - calculate_squad_value(myfootballers)
    else:
        budget = 150000000

    myfootballers = MyFootballer.objects.filter(
        owner=request.user, matchday=transfer_matchday
    )
    matchday_number = Match.objects.all().count()
    if myfootballers.count() >= (15 * matchday_number):
        have_played = True
    else:
        have_played = False

    context = {
        "Footballer": footballers,
        "Matchdays": matchdays,
        "MyFootballer": myfootballers,
        "matchdayID": transfer_matchday.id,
        "budget": budget,
        "HavePlayed": have_played,
    }
    return render(request, template_name, context)


@login_required
def footballerAddFirst(request):
    if request.method == "POST":
        matchdayID = request.POST.get("mday_id")
        footballer_id = request.POST.get("footballer_id")
        footballer = Footballer.objects.get(id=footballer_id)
        first_squad = MyFootballer.objects.filter(
            matchday_id=matchdayID, owner=request.user, squad_role="FS"
        )
        myfootballers = MyFootballer.objects.filter(
            matchday_id=matchdayID, owner=request.user
        )
        budget = 150000000 - calculate_squad_value(myfootballers)
        this_matchday = Matchday.objects.get(id=matchdayID)

        squadrole = "FS"
        position = footballer.position
        goalkeepers_number = MyFootballer.objects.filter(
            footballer__position__contains="GK",
            matchday_id=matchdayID,
            owner=request.user,
        ).count()
        fs_forwards_number = MyFootballer.objects.filter(
            footballer__position__contains="FW",
            matchday_id=matchdayID,
            owner=request.user,
            squad_role="FS",
        ).count()
        fs_defenders_number = MyFootballer.objects.filter(
            footballer__position__contains="DF",
            matchday_id=matchdayID,
            owner=request.user,
            squad_role="FS",
        ).count()

        if fs_forwards_number < 1 and position == "FW" and first_squad.count() == 10:
            squadrole = "FS"
        elif fs_defenders_number < 3 and position == "DF" and first_squad.count() == 10:
            squadrole = "FS"
        elif position == "MF" and (
            (
                fs_defenders_number < 3
                and first_squad.count() == (11 - (3 - fs_defenders_number))
            )
            or (fs_forwards_number < 1)
            and first_squad.count() == 10
        ):
            if myfootballers.filter(squad_role="SUB2").exists():
                squadrole = "SUB3"
            elif myfootballers.filter(squad_role="SUB1").exists():
                squadrole = "SUB2"
            else:
                squadrole = "SUB1"
        elif position != "GK":
            if first_squad.count() >= 11:
                if myfootballers.filter(squad_role="SUB2").exists():
                    squadrole = "SUB3"
                elif myfootballers.filter(squad_role="SUB1").exists():
                    squadrole = "SUB2"
                else:
                    squadrole = "SUB1"
        elif goalkeepers_number > 0:
            squadrole = "SUBB"
        squadowner = request.user

        newfootballer = MyFootballer.objects.filter(
            footballer_id=footballer_id, matchday_id=matchdayID, owner=squadowner
        )
        if newfootballer.exists():
            return JsonResponse({"status": "error_exists"})

        defenders_number = MyFootballer.objects.filter(
            footballer__position__contains="DF",
            matchday_id=matchdayID,
            owner=request.user,
        ).count()
        midfielders_number = MyFootballer.objects.filter(
            footballer__position__contains="MF",
            matchday_id=matchdayID,
            owner=request.user,
        ).count()
        forwards_number = MyFootballer.objects.filter(
            footballer__position__contains="FW",
            matchday_id=matchdayID,
            owner=request.user,
        ).count()
        if goalkeepers_number >= 2 and footballer.position == "GK":
            return JsonResponse({"status": "error_gk"})
        if defenders_number >= 5 and footballer.position == "DF":
            return JsonResponse({"status": "error_df"})
        if midfielders_number >= 5 and footballer.position == "MF":
            return JsonResponse({"status": "error_mf"})
        if forwards_number >= 3 and footballer.position == "FW":
            return JsonResponse({"status": "error_fw"})

        if (budget - footballer.price) < 0:
            return JsonResponse({"status": "error_val"})

        if isMatchdayFinished(this_matchday):
            return JsonResponse({"status": "error_date"})

        matchdays = Matchday.objects.all()
        for mday in matchdays:
            if mday.start_date.timestamp() > d.datetime.now().timestamp():
                newfootballer = MyFootballer.objects.create(
                    footballer_id=footballer_id,
                    matchday_id=mday.id,
                    squad_role=squadrole,
                    owner=squadowner,
                )
        return redirect("/transferFirst/")


@login_required
def adminControlDashboard(request, template_name="admincontrol.html"):
    teams = Team.objects.all()
    matchdays = Matchday.objects.all()
    matches = Match.objects.all()
    matches_ordered = matches.order_by("-id")
    context = {"Teams": teams, "Matchdays": matchdays, "Matches": matches_ordered}
    return render(request, template_name, context)


@login_required
def createMatch(request):
    if request.method == "POST":
        HomeTeamID = request.POST.get("hometeam")
        AwayTeamID = request.POST.get("awayteam")
        MatchdayID = request.POST.get("matchday")
        HomeTeam = Team.objects.get(id=HomeTeamID)
        AwayTeam = Team.objects.get(id=AwayTeamID)
        matches = Match.objects.all()
        if HomeTeam == AwayTeam:
            return redirect("/admindashboard")
        newmatch = Match.objects.create(
            HomeTeam_id=HomeTeamID, AwayTeam_id=AwayTeamID, Matchday_id=MatchdayID
        )
        return redirect("/admindashboard")


@login_required
def delete_match(request):
    match_ID = request.POST.get("matchID")
    match_to_delete = Match.objects.get(id=match_ID)
    match_to_delete.delete()
    return redirect("/admindashboard")


@login_required
def matchManage(request, id, template_name="managematch.html"):
    events = MatchEvent.objects.all()
    match = Match.objects.get(id=id)
    team1 = match.HomeTeam
    team2 = match.AwayTeam
    team1players = team1.footballers.all()
    team2players = team2.footballers.all()
    context = {
        "events": events,
        "HomePlayers": team1players,
        "AwayPlayers": team2players,
        "Match": match,
    }
    return render(request, template_name, context)


@login_required
def add_starting_home(request):
    if request.method == "POST":
        matchID = request.POST.get("matchID")
        footballerID = request.POST.get("footballerID")
        footballer = Footballer.objects.get(id=footballerID)
        match = Match.objects.get(id=matchID)
        match.HomePlayed.add(footballer)
        return redirect("/matchManage/%s" % matchID)


@login_required
def add_starting_away(request):
    if request.method == "POST":
        matchID = request.POST.get("matchID")
        footballerID = request.POST.get("footballerID")
        footballer = Footballer.objects.get(id=footballerID)
        match = Match.objects.get(id=matchID)
        match.AvayPlayed.add(footballer)
        return redirect("/matchManage/%s" % matchID)


@login_required
def addMatchEvent(request):
    if request.method == "POST":
        matchID = request.POST.get("matchID")
        eventID = request.POST.get("eventID")
        footballerID = request.POST.get("footballerID")
        match = Match.objects.get(id=matchID)
        event = FootballersAction.objects.create(
            event_id=eventID, footballer_id=footballerID
        )
        match.event.add(event)
        return redirect("/matchManage/%s" % matchID)


@login_required
def transferFootballer(request, id, template_name="maketransfer.html"):
    player_out = MyFootballer.objects.get(id=id)
    footballers = Footballer.objects.filter(position=player_out.footballer.position)
    matchday = player_out.matchday
    matchdays = Matchday.objects.all()
    transfer_matchday = None
    for mday in matchdays:
        if (not isMatchdayFinished(mday)) and (not isMatchdayStarted(mday)):
            transfer_matchday = mday
            break
    myfootballers = MyFootballer.objects.filter(
        owner=request.user,
        matchday=transfer_matchday,
        footballer__position__contains=player_out.footballer.position,
    )
    myfootballers_set = [item.footballer for item in myfootballers]
    newfootballers = [item for item in footballers if item not in myfootballers_set]
    transfers = Transfer.objects.filter(owner=request.user.id, matchday=matchday)
    context = {
        "playerOut": player_out,
        "Footballers": footballers,
        "Transfers": transfers,
        "Matchday": matchday,
        "MyFootballers": myfootballers,
        "NewFootballers": newfootballers,
    }
    return render(request, template_name, context)


@login_required
def makeTransfer(request):
    player_in_ID = request.POST.get("playerinID")
    player_out_ID = request.POST.get("playeroutID")
    player_out = MyFootballer.objects.get(id=player_out_ID)
    matchday = player_out.matchday
    player_in = Footballer.objects.get(id=player_in_ID)
    player_out_team = player_out.footballer.team
    player_in_team = player_in.team
    club_set_out = player_out_team.footballers.all()
    club_set_in = player_in_team.footballers.all()
    club_number_out = 0
    club_number_in = 0
    myfootballers = MyFootballer.objects.filter(matchday=matchday, owner=request.user)
    for mfoot in myfootballers:
        for club_player in club_set_out:
            if mfoot.footballer == club_player:
                club_number_out += 1
        for club_player_in in club_set_in:
            if mfoot.footballer == club_player_in:
                club_number_in += 1
    squad = MyFootballer.objects.filter(owner=request.user, matchday=matchday)
    budget = 150000000 - calculate_squad_value(squad)
    new_budget = budget + player_out.footballer.price - player_in.price
    transfers = Transfer.objects.filter(owner=request.user.id, matchday=matchday)
    transfers_left = 3 - transfers.count()

    matchdays = Matchday.objects.all()

    if transfers_left >= 1:
        if new_budget <= 150000000:
            if (
                player_out.footballer.team == player_in.team
                or club_number_in < matchday.same_team_max
            ):
                if player_out.footballer.position == player_in.position:
                    new_transfer = Transfer(
                        player_out=player_out.footballer,
                        player_in=player_in,
                        owner=request.user,
                        matchday=matchday,
                    )
                    new_transfer.save()
                    for mday in matchdays:
                        if mday.start_date.timestamp() > d.datetime.now().timestamp():
                            MyFootballer.objects.filter(
                                footballer=player_out.footballer, matchday_id=mday.id
                            ).delete()
                            MyFootballer.objects.create(
                                footballer_id=player_in.id,
                                matchday=mday,
                                owner=request.user,
                                squad_role=player_out.squad_role,
                            )
                    return redirect("/transfer/")
                else:
                    return JsonResponse({"status": "err_pos"})
            else:
                return JsonResponse({"status": "err_max"})
        return JsonResponse({"status": "err_bud"})
    return JsonResponse({"status": "err_trans"})


@login_required
def transfer(request, template_name="footballertransfer.html"):
    matchdays = Matchday.objects.all()
    transfer_matchday = None
    for mday in matchdays:
        if (not isMatchdayFinished(mday)) and (not isMatchdayStarted(mday)):
            transfer_matchday = mday
            break
    myfootballers = MyFootballer.objects.filter(
        owner=request.user, matchday=transfer_matchday
    )
    transfers = Transfer.objects.filter(
        owner=request.user.id, matchday=transfer_matchday
    )
    transfers_left = 3 - transfers.count()

    context = {
        "Matchday": transfer_matchday,
        "MyFootballers": myfootballers,
        "TransfersLeft": transfers_left,
    }
    return render(request, template_name, context)


@login_required
def substitutions(request, template_name="makesubs.html"):
    current_matchday = None
    matchdays = Matchday.objects.all()
    for mday in matchdays:
        if (not isMatchdayFinished(mday)) and (not isMatchdayStarted(mday)):
            current_matchday = mday
            break
    if current_matchday == None:
        return redirect("/noMatchday")
    does_exist = MyFootballer.objects.filter(matchday=current_matchday)
    first_squad = None
    sub_keeper = None
    first_sub = None
    second_sub = None
    third_sub = None
    if does_exist.exists():
        first_squad = MyFootballer.objects.filter(
            owner=request.user, matchday=current_matchday, squad_role="FS"
        )
        sub_keeper = MyFootballer.objects.get(
            owner=request.user, matchday=current_matchday, squad_role="SUBB"
        )
        first_sub = MyFootballer.objects.get(
            owner=request.user, matchday=current_matchday, squad_role="SUB1"
        )
        second_sub = MyFootballer.objects.get(
            owner=request.user, matchday=current_matchday, squad_role="SUB2"
        )
        third_sub = MyFootballer.objects.get(
            owner=request.user, matchday=current_matchday, squad_role="SUB3"
        )

    supersubs = PowerUp.objects.filter(
        matchday=current_matchday, owner=request.user, powerup_type="SC"
    )
    triplecaptains = PowerUp.objects.filter(
        matchday=current_matchday, owner=request.user, powerup_type="TC"
    )

    defenders = MyFootballer.objects.filter(
        owner=request.user,
        matchday=current_matchday,
        squad_role="FS",
        footballer__position__contains="DF",
    )
    strikers = MyFootballer.objects.filter(
        owner=request.user,
        matchday=current_matchday,
        squad_role="FS",
        footballer__position__contains="FW",
    )
    enough_defenders = True
    enough_strikers = True
    if strikers.count() == 1:
        enough_strikers = False
    if defenders.count() == 3:
        enough_defenders = False
    context = {
        "first_squad": first_squad,
        "sub_keeper": sub_keeper,
        "first_sub": first_sub,
        "second_sub": second_sub,
        "third_sub": third_sub,
        "enough_strikers": enough_strikers,
        "enough_defenders": enough_defenders,
        "supersubs": supersubs,
        "triplecaptains": triplecaptains,
        "matchday": current_matchday,
    }
    return render(request, template_name, context)


@login_required
def subView(request, id, template_name="subView.html"):
    player_off = MyFootballer.objects.get(id=id)
    matchdays = Matchday.objects.all()
    current_matchday = None
    for mday in matchdays:
        if (not isMatchdayFinished(mday)) and (not isMatchdayStarted(mday)):
            current_matchday = mday
            break
    defenders = MyFootballer.objects.filter(
        owner=request.user,
        matchday=current_matchday,
        squad_role="FS",
        footballer__position__contains="DF",
    )
    strikers = MyFootballer.objects.filter(
        owner=request.user,
        matchday=current_matchday,
        squad_role="FS",
        footballer__position__contains="FW",
    )
    enough_defenders = True
    enough_strikers = True
    if strikers.count() == 1:
        enough_strikers = False
    if defenders.count() == 3:
        enough_defenders = False

    does_exist = MyFootballer.objects.filter(matchday=current_matchday)
    sub_keeper = None
    first_sub = None
    second_sub = None
    third_sub = None
    if does_exist.exists():
        sub_keeper = MyFootballer.objects.get(
            owner=request.user, matchday=current_matchday, squad_role="SUBB"
        )
        first_sub = MyFootballer.objects.get(
            owner=request.user, matchday=current_matchday, squad_role="SUB1"
        )
        second_sub = MyFootballer.objects.get(
            owner=request.user, matchday=current_matchday, squad_role="SUB2"
        )
        third_sub = MyFootballer.objects.get(
            owner=request.user, matchday=current_matchday, squad_role="SUB3"
        )
    context = {
        "sub_keeper": sub_keeper,
        "first_sub": first_sub,
        "second_sub": second_sub,
        "third_sub": third_sub,
        "player_off": player_off,
        "enough_strikers": enough_strikers,
        "enough_defenders": enough_defenders,
    }

    return render(request, template_name, context)


@login_required
def subOnOff(request):
    player_off_ID = request.POST.get("playerOff")
    player_in_ID = request.POST.get("playerIn")
    player_off = MyFootballer.objects.filter(id=player_off_ID)
    player_off_get = MyFootballer.objects.get(id=player_off_ID)
    player_in_get = MyFootballer.objects.get(id=player_in_ID)
    matchday = player_off_get.matchday
    player_in = MyFootballer.objects.filter(id=player_in_ID)
    new_role = MyFootballer.objects.get(id=player_in_ID).squad_role
    footballer = MyFootballer.objects.get(id=player_off_ID, matchday=matchday)
    position = footballer.footballer.position
    enough_defenders = request.POST.get("enoughDF")
    enough_strikers = request.POST.get("enoughFW")
    if (position == "GK" and new_role != "SUBB") or (
        position != "GK" and new_role == "SUBB"
    ):
        return JsonResponse({"status": "err_gk"})
    if (
        enough_defenders == "False"
        and player_in_get.footballer.position != "DF"
        and position == "DF"
    ):
        return JsonResponse({"status": "error_posdf"})
    elif (
        enough_strikers == "False"
        and player_in_get.footballer.position != "FW"
        and position == "FW"
    ):
        return JsonResponse({"status": "error_posfw"})
    player_off.update(squad_role=None)
    player_in.update(squad_role="FS")
    player_off.update(squad_role=new_role)
    return redirect("/makeSubs/")


@login_required
def bonus_create(request):
    bonus_type = request.POST.get("bonusType")
    matchday_id = request.POST.get("matchdayID")
    check_new_bonus = PowerUp.objects.filter(
        owner=request.user, powerup_type=bonus_type
    )
    matchday_bonuses = PowerUp.objects.filter(
        owner=request.user, matchday_id=matchday_id
    ).count()
    if check_new_bonus.exists() or matchday_bonuses >= 1:
        return JsonResponse({"status": "already used"})
    else:
        new_bonus = PowerUp.objects.create(
            owner=request.user,
            matchday_id=matchday_id,
            powerup_type=bonus_type,
            is_used=True,
        )
        return JsonResponse({"status": "created"})


@login_required
def bonus_delete(request):
    bonus_type = request.POST.get("bonusType")
    matchday_id = request.POST.get("matchdayID")
    delete_bonus = PowerUp.objects.filter(
        owner=request.user,
        matchday_id=matchday_id,
        powerup_type=bonus_type,
        is_used=True,
    ).delete()
    return JsonResponse({"status": "deleted"})


@login_required
def set_captain(request):
    matchday = request.POST.get("matchday")
    footballerID = request.POST.get("footballerID")

    footballer = MyFootballer.objects.get(id=footballerID)
    captain_role = request.POST.get("captain")
    current_captain_exists = MyFootballer.objects.filter(
        matchday=matchday, captain=True, owner=request.user
    )
    if current_captain_exists:
        current_captain = MyFootballer.objects.get(
            matchday=matchday, captain=True, owner=request.user
        )
    current_vice_captain_exists = MyFootballer.objects.filter(
        matchday=matchday, vice_captain=True, owner=request.user
    )
    if current_vice_captain_exists:
        current_vice_captain = MyFootballer.objects.get(
            matchday=matchday, vice_captain=True, owner=request.user
        )
    if captain_role == "C":
        if current_captain_exists:
            if footballer != current_captain and footballer != current_vice_captain:
                current_captain.captain = False
                current_captain.save()
                footballer.captain = True
                footballer.save()
                return redirect("/makeSubs/")
        else:
            footballer.captain = True
            footballer.save()
            return redirect("/makeSubs/")
    if captain_role == "VC":
        if current_vice_captain_exists:
            if footballer != current_vice_captain and footballer != current_captain:
                current_vice_captain.vice_captain = False
                current_vice_captain.save()
                footballer.vice_captain = True
                footballer.save()
                return redirect("/makeSubs/")
        else:
            footballer.vice_captain = True
            footballer.save()
            return redirect("/makeSubs/")
    return redirect("/makeSubs/")

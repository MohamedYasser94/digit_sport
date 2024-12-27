import requests
from django.contrib import messages
from django.contrib.admin.templatetags.admin_list import pagination
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from apps.sport.forms.forms import *
from apps.sport.forms.monk import *
from apps.sport.models.models import *
from apps.sport.models.monks import *
from core.models.core import CommonTranslate
from digit_sport import settings
from helper.commonHelper import BACKEND_TEMPLATES
from helper.decorators import authenticated_staf, staff_only

User = get_user_model()
api_key = settings.SPORT_MONKS_TOKEN
base_url = settings.SPORT_MONKS_URL

@authenticated_staf
@staff_only
def AdminMonksCountryList(request):
    countries = MonkCountry.objects.all()

    if request.method == "POST":
        teams_form = AdminTeamsForm(request.POST or None, request.FILES or None)

        if teams_form:
            name = request.POST.get('name')
            short_code = request.POST.get('short_code')
            country = request.POST.get('country')
            club = request.POST.get('club')
            sport = request.POST.get('sport')
            venue = request.POST.get('venue')
            gender = request.POST.get('gender')
            keyword = request.POST.get('keyword')

            image = request.FILES.get('image')
            image_path = request.POST.get('image_path')
            status = 'Active'

            try:
                check_teams = Teams.objects.get(name=name)
                messages.error(request, _("Teams Already Exist , Please Try Again"), extra_tags='Teams')
                return HttpResponseRedirect(reverse_lazy('sport:AdminTeamsList'))
            except:
                pass



            if venue == None or venue == '':
                venue = None
            else:
                venue = Venues.objects.get(id=venue)

            if club == None or club == '':
                club = None
            else:
                club = Clubs.objects.get(id=club)

            if sport == None or sport == '':
                sport = None
            else:
                sport = Sport.objects.get(id=sport)




            teams_object = Teams(  name=name,country=country,club=club,sport=sport,venue=venue,
                                   gender=gender,keyword=keyword,short_code=short_code,image=image,
                                      image_path=image_path,status='Active')

            teams_object.save()
            messages.success(request, _("Teams Add Successfully"), extra_tags='Teams')

            return HttpResponseRedirect(reverse_lazy('sport:AdminTeamsList'))
        else:

            messages.error(request, _("Teams Not Add , Please Try Again"), extra_tags='Teams')

    else:
        context = {'countries': countries, 'teams_form': AdminTeamsForm(), 'current_page': _('Teams')

                   }
        return render(request, f'{BACKEND_TEMPLATES}/monks/country/admin.html', context)



@csrf_exempt
def AdminMonksCountryGetData(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "POST":
        monk_country_form = AdminMonkCountryForm(request.POST or None, request.FILES or None)
        if monk_country_form:
            page = request.POST.get('pages')
            i = 1
            for i in range(int(page)):
                i = i + 1
                response = requests.get(
                    base_url + f'core/countries?page={i}&api_token={api_key}',
                    headers={
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        "Authorization": f"Bearer {api_key}",
                    },
                )

                if response.status_code == 200:
                    data = response.json()
                    data_to_db = data['data']
                    for data in data_to_db:
                        try:
                            check_country = MonkCountry.objects.get(name=data['name'])
                            check_country.api_id = data['id']
                            check_country.name = data['name']
                            check_country.official_name = data['official_name']
                            check_country.fifa_name = data['fifa_name']
                            check_country.iso2 = data['iso2']
                            check_country.iso3 = data['iso3']
                            check_country.latitude = data['latitude']
                            check_country.longitude = data['longitude']
                            check_country.image_path = data['image_path']
                            check_country.borders = data['borders']
                            check_country.save()
                        except:
                            country_object = MonkCountry(api_id=data['id'], name=data['name'],
                                                          official_name=data['official_name'],
                                                         fifa_name=data['fifa_name'], iso2=data['iso2'], iso3=data['iso3'],
                                                         latitude=data['latitude'], longitude=data['longitude'],
                                                         image_path=data['image_path'], borders=data['borders'],
                                                        )
                            country_object.save()


            data = {'type': 'Success', 'message': 'Data Add Successfully'}

            return JsonResponse(data=data, safe=False)


        else:
           data = {'type': 'Error', 'message': f'Data Not Add Successfully '}
           return JsonResponse(data=data, safe=False)
    else:
        data = {'type': 'Error', 'message': 'Data Not Add Successfully '}
        return JsonResponse(data=data, safe=False)


@csrf_exempt
def AdminMonksLeaguesGetData(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "POST":
        teams_form = AdminTeamsForm(request.POST or None, request.FILES or None)
        data = ''
        if teams_form:
            page = request.POST.get('pages')


            try:
                sport_id = Sport.objects.get_or_create(name='football')
                sport_id = Sport.objects.get(name='football')
            except:
                sport_id = None
            i = 1
            for i in range(int(page)):

                i = i + 1

                response = requests.get(
                    base_url + f'football/leagues?page={i}&api_token={api_key}&include=today;currentSeason;country',
                    headers={
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        "Authorization": f"Bearer {api_key}",
                    },
                )

                if response.status_code == 200:
                    data = response.json()

                    data_to_db = data['data']

                    for data in data_to_db:
                        try:
                            country = data['country']['name']
                            country_image = data['country']['image_path']
                        except:
                            country = None
                            country_image = None
                        try:
                            currentseason = data['currentseason']['id']
                        except:
                            currentseason = None

                        try:

                            check_leagues = Leagues.objects.get(name=data['name'])
                            check_leagues.api_id = data['id']
                            check_leagues.name = data['name']
                            check_leagues.name_tr = data['name']
                            check_leagues.short_code = data['short_code']
                            check_leagues.api_country = data['country_id']
                            check_leagues.sport = sport_id.id
                            check_leagues.image_path = data['image_path']
                            check_leagues.api_active = data['active']
                            check_leagues.type = data['type']
                            check_leagues.sub_type = data['sub_type']
                            check_leagues.api_category = data['category']
                            check_leagues.last_played_at = data['last_played_at']
                            check_leagues.has_jerseys = data['has_jerseys']
                            check_leagues.country = country
                            check_leagues.country_image = country_image
                            check_leagues.currentseason = currentseason
                            check_leagues.keyword = data
                            check_leagues.save()
                        except Exception as e:
                            print('error',e)
                            leagues_object = Leagues(api_id=data['id'], name=data['name'],name_tr=data['name'],
                                                     sport_id=sport_id.id,
                                                    short_code=data['short_code'],api_country=data['country_id'],
                                                    sport=sport_id,image_path=data['image_path'],
                                                    type=data['type'],api_active=data['active'],
                                                    sub_type=data['sub_type'],api_category=data['category'],
                                                    last_played_at=data['last_played_at'],has_jerseys=data['has_jerseys'],
                                                    country=country,country_image=country_image,
                                                    currentseason=currentseason, keyword=data)
                            leagues_object.save()
                    data = {'type': 'Success', 'message': 'Data Add Successfully'}
                else:
                    data = {'type': 'Error', 'message': f'Data Not Add Successfully Response Code {response.status_code} '}




            return JsonResponse(data=data, safe=False)


        else:
           data = {'type': 'Error', 'message': f'Data Not Add Successfully '}
           return JsonResponse(data=data, safe=False)
    else:
        data = {'type': 'Error', 'message': 'Data Not Add Successfully '}
        return JsonResponse(data=data, safe=False)


@csrf_exempt
def AdminMonksSeasonGetData(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "POST":
        teams_form = AdminTeamsForm(request.POST or None, request.FILES or None)
        data = ''
        if teams_form:
            page = request.POST.get('pages')
            sport = request.POST.get('sport')

            try:
                sport_id = Sport.objects.get(name=sport)
            except:
                sport_id = None
            i = 1
            for i in range(int(page)):

                i = i + 1

                response = requests.get(
                    base_url + f'{sport}/seasons?page={i}&api_token={api_key}',
                    headers={
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        "Authorization": f"Bearer {api_key}",
                    },
                )

                if response.status_code == 200:
                    data = response.json()

                    data_to_db = data['data']

                    for data in data_to_db:

                        try:
                            try:
                                league = Leagues.objects.get(api_id=data['league_id'])
                            except:
                                league = None

                            check_season = Season.objects.get(name=data['name'])
                            check_season.api_id = data['id']
                            check_season.name = data['name']
                            check_season.sport = sport_id
                            check_season.league = league
                            check_season.tie_breaker_rule = data['tie_breaker_rule_id']
                            check_season.finished = data['finished']
                            check_season.pending = data['pending']
                            check_season.is_current = data['is_current']
                            check_season.starting_at = data['starting_at']
                            check_season.ending_at = data['ending_at']
                            check_season.standings_recalculated_at = data['standings_recalculated_at']
                            check_season.games_in_current_week = data['games_in_current_week']
                            check_season.save()
                        except:
                            try:
                                league = Leagues.objects.get(api_id=data['league_id'])
                            except:
                                league = None
                            season_object = Season(api_id=data['id'], name=data['name'],
                                                    sport=sport_id,league=league,
                                                    tie_breaker_rule=data['tie_breaker_rule_id'],
                                                    finished=data['finished'],pending=data['pending'],
                                                    is_current=data['is_current'],starting_at=data['starting_at'],
                                                    ending_at=data['ending_at'],
                                                    standings_recalculated_at=data['standings_recalculated_at'],
                                                    games_in_current_week=data['games_in_current_week'],


                                                     )
                            season_object.save()
                    data = {'type': 'Success', 'message': 'Data Add Successfully'}
                else:
                    data = {'type': 'Error',
                            'message': f'Data Not Add Successfully Response Code {response.status_code} '}

            return JsonResponse(data=data, safe=False)


        else:
            data = {'type': 'Error', 'message': f'Data Not Add Successfully '}
            return JsonResponse(data=data, safe=False)
    else:
        data = {'type': 'Error', 'message': 'Data Not Add Successfully '}
        return JsonResponse(data=data, safe=False)


@csrf_exempt
def AdminMonksStagesGetData(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "POST":
        stages_form = AdminStagesForm(request.POST or None, request.FILES or None)
        data = ''
        if stages_form:
            page = request.POST.get('pages')
            sport = request.POST.get('sport')

            try:
                sport_id = Sport.objects.get(name=sport)
            except:
                sport_id = None
            i = 1
            for i in range(int(page)):

                i = i + 1

                response = requests.get(
                    base_url + f'{sport}/stages?page={i}&api_token={api_key}',
                    headers={
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        "Authorization": f"Bearer {api_key}",
                    },
                )

                if response.status_code == 200:
                    data = response.json()

                    data_to_db = data['data']

                    for data in data_to_db:

                        try:
                            try:
                                league = Leagues.objects.get(api_id=data['league_id'])
                            except:
                                league = None

                            try:
                                season = Season.objects.get(api_id=data['season_id'])
                            except:
                                season = None

                            check_stages = Stages.objects.get(name=data['name'])
                            check_stages.api_id = data['id']
                            check_stages.sport = sport_id
                            check_stages.league = league
                            check_stages.season = season
                            check_stages.type = data['type_id']
                            check_stages.name = data['name']
                            check_stages.sort_order = data['sort_order']
                            check_stages.finished = data['finished']
                            check_stages.is_current = data['is_current']
                            check_stages.starting_at = data['starting_at']
                            check_stages.ending_at = data['ending_at']

                            check_stages.games_in_current_week = data['games_in_current_week']
                            check_stages.tie_breaker_rule = data['tie_breaker_rule_id']
                            check_stages.save()
                        except:
                            try:
                                league = Leagues.objects.get(api_id=data['league_id'])
                            except:
                                league = None
                            try:
                                season = Season.objects.get(api_id=data['season_id'])
                            except:
                                season = None
                            stages_object = Stages(api_id=data['id'], sport=sport_id,
                                                    league=league,season=season,
                                                    type=data['type_id'],name=data['name'],
                                                    sort_order=data['sort_order'],finished=data['finished'],
                                                    is_current=data['is_current'],starting_at=data['starting_at'],
                                                    ending_at=data['ending_at'],
                                                    games_in_current_week=data['games_in_current_week'],
                                                    tie_breaker_rule=data['tie_breaker_rule_id'],

                                                         )
                            stages_object.save()
                    data = {'type': 'Success', 'message': 'Data Add Successfully'}
                else:
                    data = {'type': 'Error',
                            'message': f'Data Not Add Successfully Response Code {response.status_code} '}

            return JsonResponse(data=data, safe=False)


        else:
            data = {'type': 'Error', 'message': f'Data Not Add Successfully '}
            return JsonResponse(data=data, safe=False)
    else:
        data = {'type': 'Error', 'message': 'Data Not Add Successfully '}
        return JsonResponse(data=data, safe=False)


@csrf_exempt
def AdminMonksRoundGetData(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "POST":
        rounds_form = AdminRoundForm(request.POST or None, request.FILES or None)
        data = ''
        if rounds_form:
            page = request.POST.get('pages')
            sport = request.POST.get('sport')

            try:
                sport_id = Sport.objects.get(name=sport)
            except:
                sport_id = None
            i = 1
            for i in range(int(page)):

                i = i + 1

                response = requests.get(
                    base_url + f'{sport}/rounds?page={i}&api_token={api_key}',
                    headers={
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        "Authorization": f"Bearer {api_key}",
                    },
                )

                if response.status_code == 200:
                    data = response.json()

                    data_to_db = data['data']

                    for data in data_to_db:

                        try:
                            try:
                                league = Leagues.objects.get(api_id=data['league_id'])
                            except:
                                league = None

                            try:
                                season = Season.objects.get(api_id=data['season_id'])
                            except:
                                season = None

                            try:
                               stage = Stages.objects.get(api_id=data['stage_id'])
                            except:
                                stage = None

                            check_round = Round.objects.get(name=data['name'])
                            check_round.api_id = data['id']
                            check_round.sport = sport_id
                            check_round.league = league
                            check_round.season = season
                            check_round.stage = stage
                            check_round.name = data['name']

                            check_round.finished = data['finished']
                            check_round.is_current = data['is_current']
                            check_round.starting_at = data['starting_at']
                            check_round.ending_at = data['ending_at']

                            check_round.games_in_current_week = data['games_in_current_week']

                            check_round.save()
                        except:
                            try:
                                league = Leagues.objects.get(api_id=data['league_id'])
                            except:
                                league = None
                            try:
                                season = Season.objects.get(api_id=data['season_id'])
                            except:
                                season = None
                            try:
                               stage = Stages.objects.get(api_id=data['stage_id'])
                            except:
                                stage = None
                            round_object = Round(api_id=data['id'], sport=sport_id,
                                                    league=league,season=season,stage=stage,
                                                    name=data['name'],
                                                    finished=data['finished'],
                                                    is_current=data['is_current'],starting_at=data['starting_at'],
                                                    ending_at=data['ending_at'],
                                                    games_in_current_week=data['games_in_current_week'],


                                                         )
                            round_object.save()
                    data = {'type': 'Success', 'message': 'Data Add Successfully'}
                else:
                    data = {'type': 'Error',
                            'message': f'Data Not Add Successfully Response Code {response.status_code} '}

            return JsonResponse(data=data, safe=False)


        else:
            data = {'type': 'Error', 'message': f'Data Not Add Successfully '}
            return JsonResponse(data=data, safe=False)
    else:
        data = {'type': 'Error', 'message': 'Data Not Add Successfully '}
        return JsonResponse(data=data, safe=False)


@csrf_exempt
def AdminMonksVenuesGetData(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "POST":
        teams_form = AdminTeamsForm(request.POST or None, request.FILES or None)
        data = ''
        if teams_form:
            page = request.POST.get('pages')
            sport = request.POST.get('sport')

            i = 1
            for i in range(int(page)):

                i = i + 1

                response = requests.get(
                    base_url + f'{sport}/venues?page={i}&api_token={api_key}',
                    headers={
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        "Authorization": f"Bearer {api_key}",
                    },
                )

                if response.status_code == 200:
                    data = response.json()

                    data_to_db = data['data']

                    for data in data_to_db:

                        try:

                            check_venues = Venues.objects.get(name=data['name'])
                            check_venues.api_id = data['id']
                            check_venues.name = data['name']
                            check_venues.api_country = data['country_id']
                            check_venues.api_city = data['city_id']
                            check_venues.address = data['address']
                            check_venues.address = data['address']
                            check_venues.latitude = data['latitude']
                            check_venues.longitude = data['longitude']
                            check_venues.capacity = data['capacity']
                            check_venues.image_path = data['image_path']
                            check_venues.city_name = data['city_name']
                            check_venues.surface = data['surface']
                            check_venues.national_team = data['national_team']

                        except:

                            venues_object = Venues(api_id=data['id'], name=data['name'],
                                                    api_country=data['country_id'],api_city=data['city_id'],
                                                    address=data['address'],latitude=data['latitude'],
                                                    longitude=data['longitude'],capacity=data['capacity'],
                                                    image_path=data['image_path'],city_name=data['city_name'],
                                                    surface=data['surface'],national_team=data['national_team'],



                                                     )
                            venues_object.save()
                    data = {'type': 'Success', 'message': 'Data Add Successfully'}
                else:
                    data = {'type': 'Error',
                            'message': f'Data Not Add Successfully Response Code {response.status_code} '}

            return JsonResponse(data=data, safe=False)


        else:
            data = {'type': 'Error', 'message': f'Data Not Add Successfully '}
            return JsonResponse(data=data, safe=False)
    else:
        data = {'type': 'Error', 'message': 'Data Not Add Successfully '}
        return JsonResponse(data=data, safe=False)


def AdminMonksTeamsList(request):
    sport = Sport.objects.get(name='football')
    teams = Teams.objects.filter(sport=sport).order_by('country')

    # Create a Paginator instance, specifying the number of objects per page
    paginator = Paginator(teams, 100)  # 10 objects per page

    # Get the current page number from the GET query string
    page_number = request.GET.get('page')


    # Try to get the page object
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        # If page number is not an integer, deliver the first page
        page_obj = paginator.page(1)
    except EmptyPage:
        # If page number is out of range, deliver the last page of results
        page_obj = paginator.page(paginator.num_pages)

    else:
        context = {
            'paginator': paginator,
            'page_obj': page_obj,
           'teams_form': AdminTeamsForm(), 'current_page': _('Teams')

                   }
        return render(request, f'{BACKEND_TEMPLATES}/sport/teams/monks.html', context)
@csrf_exempt
def AdminMonksTeamsGetData(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "POST":
        teams_form = AdminTeamsForm(request.POST or None, request.FILES or None)
        data = ''
        if teams_form:
            page = request.POST.get('pages')
            sport = request.POST.get('sport')
            print('sport',sport)

            try:
                sport_id = Sport.objects.get(name=sport)
            except:
                sport_id = None
            i = 1
            for i in range(int(page)):

                i = i + 1

                response = requests.get(
                    base_url + f'{sport}/teams?page={i}&api_token={api_key}&include=country',
                    headers={
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        "Authorization": f"Bearer {api_key}",
                    },
                )

                if response.status_code == 200:
                    data = response.json()

                    data_to_db = data['data']

                    for data in data_to_db:
                        try:
                            country = data['country']['name']
                            country_image = data['country']['image_path']
                        except:
                            country = None
                            country_image = None
                        try:
                            currentseason = data['currentseason']['id']
                        except:
                            currentseason = None

                        try:
                            check_teams = Teams.objects.get(api_id=data['id'])
                            check_teams.api_id = data['id']
                            check_teams.name = data['name']
                            check_teams.short_code = data['short_code']
                            check_teams.api_country = data['country_id']
                            check_teams.api_venue = data['venue_id']
                            check_teams.sport = sport_id
                            check_teams.gender = data['gender']
                            check_teams.founded = data['founded']
                            check_teams.type = data['type']
                            check_teams.placeholder = data['placeholder']
                            check_teams.last_played_at = data['last_played_at']
                            check_teams.country = country
                            check_teams.country_image = country_image
                            check_teams.keyword = data
                            # check_teams.save()
                        except:
                            teams_object = Teams(api_id=data['id'], name=data['name'],name_tr=data['name'],
                                                 short_code=data['short_code'],api_country=data['country_id'], api_venue=data['venue_id'],
                                                sport=sport_id,gender=data['gender'],image_path=data['image_path'],
                                                    founded=data['founded'],type=data['type'],placeholder=data['placeholder'],
                                                    last_played_at=data['last_played_at'],country=country,country_image=country_image,
                                                 keyword=data
                                                 )
                            teams_object.save()
                    data = {'type': 'Success', 'message': 'Data Add Successfully'}
                else:
                    data = {'type': 'Error', 'message': f'Data Not Add Successfully Response Code {response.status_code} '}




            return JsonResponse(data=data, safe=False)


        else:
           data = {'type': 'Error', 'message': f'Data Not Add Successfully '}
           return JsonResponse(data=data, safe=False)
    else:
        data = {'type': 'Error', 'message': 'Data Not Add Successfully '}
        return JsonResponse(data=data, safe=False)


@csrf_exempt
def AdminMonksPlayersGetData(request):
    if not request.user.is_authenticated:
        return HttpResponse(status=status.HTTP_401_UNAUTHORIZED)

    if request.method == "POST":
        teams_form = AdminTeamsForm(request.POST or None, request.FILES or None)
        data = ''
        if teams_form:
            page = request.POST.get('pages')
            sport = request.POST.get('sport')

            try:
                sport_id = Sport.objects.get(name=sport)
            except:
                sport_id = None
            i = 1
            for i in range(int(page)):

                i = i + 1

                response = requests.get(
                    base_url + f'{sport}/players?page={i}&api_token={api_key}',
                    headers={
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        "Authorization": f"Bearer {api_key}",
                    },
                )

                if response.status_code == 200:
                    data = response.json()

                    data_to_db = data['data']

                    for data in data_to_db:

                        try:

                            check_player = Players.objects.get(name=data['name'])

                            check_player.api_id = data['id']
                            check_player.sport = sport_id
                            check_player.api_country = data['country_id']
                            check_player.api_nationality = data['nationality_id']
                            check_player.api_city = data['city_id']
                            check_player.api_position = data['position_id']
                            check_player.api_detailed_position = data['detailed_position_id']
                            check_player.type = data['type_id']
                            check_player.common_name = data['common_name']
                            check_player.first_name = data['firstname']
                            check_player.last_name = data['lastname']
                            check_player.name = data['name']
                            check_player.display_name = data['display_name']
                            check_player.image_path = data['image_path']
                            check_player.height = data['height']
                            check_player.weight = data['weight']
                            check_player.birthdate = data['date_of_birth']
                            check_player.gender = data['gender']
                            check_player.save()
                        except:
                            player_object = Players(api_id=data['id'], sport=sport_id,
                                                    api_country=data['country_id'],
                                                    api_nationality=data['nationality_id'],
                                                    api_city=data['city_id'],api_position=data['position_id'],
                                                    api_detailed_position=data['detailed_position_id'],
                                                    type=data['type_id'],common_name=data['common_name'],
                                                    first_name=data['firstname'],last_name=data['lastname'],
                                                    name=data['name'],display_name=data['display_name'],
                                                    image_path=data['image_path'],height=data['height'],
                                                    weight=data['weight'],birthdate=data['date_of_birth'],
                                                    gender=data['gender']


                                                 )
                            player_object.save()
                    data = {'type': 'Success', 'message': 'Data Add Successfully'}
                else:
                    data = {'type': 'Error', 'message': f'Data Not Add Successfully Response Code {response.status_code} '}




            return JsonResponse(data=data, safe=False)


        else:
           data = {'type': 'Error', 'message': f'Data Not Add Successfully '}
           return JsonResponse(data=data, safe=False)
    else:
        data = {'type': 'Error', 'message': 'Data Not Add Successfully '}
        return JsonResponse(data=data, safe=False)


@csrf_exempt
def AdminMonksFixturesGetData(request):
    print('sportIndex',request)

    fixtures_form = AdminFixturesForm(request.POST or None, request.FILES or None)
    data = ''
    if fixtures_form:
        page = request.POST.get('pages')
        sport = request.POST.get('sport')

        try:
            sport_id = Sport.objects.get(name=sport)
        except:
            sport_id = None
        i = 1
        for i in range(int(page)):

            i = i + 1

            response = requests.get(
                base_url + f'{sport}/fixtures?&api_token={api_key}',
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    "Authorization": f"Bearer {api_key}",
                },
            )

            if response.status_code == 200:
                data = response.json()
                print('data',data)

                data_to_db = data['data']

                # for data in data_to_db:
                #
                #     try:
                #
                #         check_fixture = Fixtures.objects.get(api_id=data['id'])
                #
                #         check_fixture.api_id = data['id']
                #         check_fixture.sport = sport_id
                #         check_fixture.api_league = data['league_id']
                #         check_fixture.api_season = data['season_id']
                #         check_fixture.api_stage = data['stage_id']
                #         check_fixture.api_group = data['group_id']
                #         check_fixture.api_aggregate = data['aggregate_id']
                #         check_fixture.api_round = data['round_id']
                #         check_fixture.api_state_id = data['state_id']
                #         check_fixture.api_venue = data['venue_id']
                #         check_fixture.name = data['name']
                #         check_fixture.time_starting_at_date = data['starting_at']['date']
                #         check_fixture.result_info = data['result_info']
                #         check_fixture.leg = data['leg']
                #         check_fixture.details = data['details']
                #         check_fixture.length = data['length']
                #         check_fixture.placeholder = data['placeholder']
                #         check_fixture.has_odds = data['has_odds']
                #         check_fixture.starting_at_timestamp = data['starting_at_timestamp']
                #         check_fixture.save()
                #     except:
                #         fixture_object = Fixtures(api_id=data['id'], sport=sport_id,
                #                                 api_league=data['league_id'],
                #                                 api_season=data['season_id'],
                #                                 api_stage=data['stage_id'],api_group=data['group_id'],
                #                                 api_aggregate=data['aggregate_id'],
                #                                 api_round=data['round_id'],api_state_id=data['state_id'],
                #                                 api_venue=data['venue_id'],name=data['name'],
                #                                 time_starting_at_date=data['starting_at']['date'],
                #                                 result_info=data['result_info'],leg=data['leg'],
                #                                 details=data['details'],length=data['length'],
                #                                 placeholder=data['placeholder'],has_odds=data['has_odds'],
                #                                 starting_at_timestamp=data['starting_at_timestamp'],
                #                                 )
                #
                #         fixture_object.save()
                data = {'type': 'Success', 'message': 'Data Add Successfully'}
            else:
                data = {'type': 'Error', 'message': f'Data Not Add Successfully Response Code {response.status_code} '}
        return JsonResponse(data=data, safe=False)
    else:
          data = {'type': 'Error', 'message': f'Data Not Add Successfully '}
          return JsonResponse(data=data, safe=False)











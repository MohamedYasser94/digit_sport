from datetime import datetime, timedelta

from django.http import JsonResponse
from rest_framework.status import *

from api.v3.serializers.sport.sport import *
from apps.sport.models.models import *
from core.models.blog import BlogArticle, BlogVideo
from core.utils.pagination import PageNumberPagination
# from core.views.notifications import AdminFcmNotifications
from digit_sport import settings

api_key = settings.SPORT_MONKS_TOKEN
base_url = settings.SPORT_MONKS_URL


#################### Matches By Leagues ##################
def LeaguesBySportAndDateApiList(request, sport_name, date, ):
    try:
        sport = Sport.objects.get(name=sport_name)
    except Exception as e:
        sport = Sport.objects.create(name=sport_name)
    league_list = []
    matches = Match.objects.filter(start_time__date=date, sport=sport.id)
    print('match count', matches.count(), date)

    for item in matches:
        league_list.append(item.league.slug)
    print('league_list', league_list, matches.count())
    league_list = Leagues.objects.filter(sport=sport.id, slug__in=league_list)

    try:
        success = True
        message = f"LeaguesBySportApiList {date}  "
        league_serializer = LeaguesWithMatchesSerializer(league_list, many=True,
                                                         context={'request': request, 'date': date})
        sport_data = {'leagues': league_serializer.data}
        data = {'success': success, 'message': message, 'data': sport_data, }
        return JsonResponse(data, safe=False, status=HTTP_200_OK)
    except Exception as e:
        print('error LeaguesBySportApiList', e)
        success = False
        message = f"error in get data   {e}  "
        sport_data = {'leagues': [], }
        data = {'success': success, 'message': message, 'data': sport_data, }
        return JsonResponse(data, safe=False, status=HTTP_204_NO_CONTENT)


def LeaguesBySportAndDateMatchesApiList(request, date, leagueid):
    league = Leagues.objects.get(id=leagueid)
    match_league = Match.objects.filter(league=leagueid, start_time__date=date)

    try:
        success = True
        message = f"Send From MatchesByDateApiList {date} "
        league_serializer = LeagueDetailsSerializer(league, many=False, context={'request': request})
        match_serializer = MatchForLeaguesByDateSerializer(match_league, many=True, context={'request': request})
        sport_data = {'league': league_serializer.data, 'matches': match_serializer.data, }

        data = {'success': success, 'data': sport_data, 'message': message, }
        return JsonResponse(data, safe=False)
    except Exception as e:
        success = False
        message = f"error in get data   {e} {date} "
        sport_data = {'matches': [], }
        data = {'success': success, 'data': sport_data, 'message': message, }
        return JsonResponse(data, safe=False, status=HTTP_404_NOT_FOUND)


def LeaguesDetailsApi(request, leagueid):
    try:
        league = Leagues.objects.get(id=leagueid)
        match_league = Match.objects.filter(league=leagueid)
        success = True
        message = f"Send From Django API mix {leagueid} "
        league_serializer = LeagueDetailsSerializer(league, many=False, context={'request': request})
        match_serializer = MatchForLeaguesByDateSerializer(match_league, many=True, context={'request': request})
        sport_data = {'league': league_serializer.data, 'matches': match_serializer.data, }

        data = {'success': success, 'data': sport_data, 'message': message, }
        return JsonResponse(data, safe=False)
    except Exception as e:
        success = False
        message = f"error in get data   {e} {leagueid} "
        sport_data = {'matches': [], }
        data = {'success': success, 'data': sport_data, 'message': message, }
        return JsonResponse(data, safe=False, status=HTTP_404_NOT_FOUND)


def LeagueMatchesByTypeApiList(request, leagueId, type):
    round_list = []
    matches_list = []
    first_date = datetime.now()
    last_date = datetime.now()

    if type == 'current':
        first_date = datetime.now()
        last_date = datetime.now() + timedelta(days=365)
        order_by = 'start_time'
        matches_list = Match.objects.filter(league=leagueId, start_time__range=[first_date, last_date]).order_by(
            order_by)
        round_list = Round.objects.filter(league=leagueId, starting_at__range=[first_date, last_date]
                                          ).order_by(
            'starting_at')
    elif type == 'past':
        first_date = datetime.now() - timedelta(days=365)
        last_date = datetime.now()
        order_by = 'start_time'
        matches_list = Match.objects.filter(league=leagueId, start_time__range=[first_date, last_date]).order_by(
            order_by)
        round_list = Round.objects.filter(league=leagueId, starting_at__range=[first_date, last_date]).order_by(
            '-starting_at')

    try:
        success = True
        message = f"Send From Django {leagueId} {type} {first_date} {last_date} "
        match_serializer = MatchForLeagueByTypeSerializer(matches_list, many=True, context={'request': request})

        round_serializer = RoundSerializer(round_list, many=True,
                                           context={'first_date': first_date, 'last_date': last_date,
                                                    'leagueId': leagueId, 'request': request})
        sport_data = {'rounds': round_serializer.data,
                      }
        data = {'success': success, 'data': sport_data, 'message': message, }
        return JsonResponse(data, safe=False)
    except Exception as e:
        success = False
        message = f"error in get data   {e} {type} "
        sport_data = {'rounds': [],

                      }

        data = {'success': success, 'data': sport_data, 'message': message,

                }
        return JsonResponse(data, safe=False)


def LeagueTeamsApiList(request, leagueId):
    try:
        league = Leagues.objects.get(id=leagueId)
        matches = Match.objects.filter(league=leagueId)
        team_list = []
        for match in matches:
            home_team = match.home_team.id
            away_team = match.away_team.id
            team_list.append(home_team)
            team_list.append(away_team)
        team_list = list(set(team_list))

        teams = Teams.objects.all().filter(id__in=team_list)

        success = True
        message = f"Send From Django API mix {leagueId} "
        league_serializer = LeagueDetailsSerializer(league, many=False, context={'request': request})
        teams_serializer = TeamsSerializer(teams, many=True, context={'request': request})
        sport_data = {'league': league_serializer.data, 'teams': teams_serializer.data, }

        data = {'success': success, 'data': sport_data, 'message': message, }

        return JsonResponse(data, safe=False)
    except Exception as e:
        success = False
        message = f"error in get data   {e}  "
        sport_data = {'league': [], 'teams': [], }
        data = {'success': success, 'data': sport_data, 'message': message, }
        return JsonResponse(data, safe=False)


def MatchDetailsApi(request, match_id):
    try:
        match = Match.objects.get(id=match_id)
        goals = MatchGoals.objects.filter(match=match_id)
        standing = TeamSeasonTable.objects.filter(league_id=match.league.id).order_by('position')
        match_serializer = MatchDetailsSerializer(match, many=False, context={'request': request})
        goals_serializer = MatchGoalsSerializer(goals, many=True, context={'request': request})
        standing_serializer = TeamSeasonTableSerializer(standing, many=True, context={'request': request})
        sport_data = {
            'matches': match_serializer.data, 'goals': goals_serializer.data,
            'table': standing_serializer.data,
        }
        success = True
        message = f"Send From Django API mix {match_id} "

        data = {'success': success, 'data': sport_data, 'message': message,

                }
        return JsonResponse(data, safe=False)

    except Exception as e:
        print(e)
        success = False
        message = f"error in get data  match Details {e} "

        sport_data = {'matches': [],

                      }

    data = {'success': success, 'data': sport_data, 'message': message,

            }
    return JsonResponse(data, safe=False)


def TeamMatchesApiList(request, team_id, day_type):
    try:
        team = Teams.objects.get(id=team_id)
        first_date = datetime.now()
        last_date = datetime.now()
        order_by = 'start_time'
        if day_type == 'current':
            first_date = datetime.now()
            last_date = datetime.now() + timedelta(days=90)
            order_by = 'start_time'
        elif day_type == 'past':
            first_date = datetime.now() - timedelta(days=90)
            last_date = datetime.now()
            order_by = 'start_time'

        match_list = Match.objects.filter(home_team=team.id, start_time__range=[first_date, last_date]).order_by(
            order_by)
        match_list_away = Match.objects.filter(away_team=team.id,
                                               start_time__range=[first_date, last_date]).order_by(
            order_by)
        match_list = match_list | match_list_away
        success = True
        message = f"Send From Django API mix {first_date} {last_date} "
        match_serializer = MatchDetailsSerializer(match_list, many=True, context={'request': request})
        sport_data = {'team': team.name, 'matches': match_serializer.data, }

        data = {'success': success, 'data': sport_data, 'message': message, }

        return JsonResponse(data, safe=False)
    except Exception as e:
        success = False
        message = f"error in get data   {e}  "
        sport_data = {'team': team_id, 'matches': [], }
        data = {'success': success, 'data': sport_data, 'message': message, }
        return JsonResponse(data, safe=False)


def SeasonTableByLeagueApiList(request, league_id):
    try:

        table_list = TeamSeasonTable.objects.filter(league_id=league_id).order_by('position')
        success = True
        message = f"Send From Django API mix table "
        table_serializer = TeamSeasonTableSerializer(table_list, many=True, context={'request': request})
        sport_data = {'sport': 'volleyball', 'table': table_serializer.data, }

        data = {'success': success, 'data': sport_data, 'message': message, }

        return JsonResponse(data, safe=False)
    except Exception as e:
        success = False
        message = f"error in get data table  {e}  "
        sport_data = {'sport': 'volleyball', 'table': [], }
        data = {'success': success, 'data': sport_data, 'message': message, }
        return JsonResponse(data, safe=False)

    ################ Old API ####################


###################### TEams Api ######################
def SportTeamsApiList(request, sport):
    try:
        sport = Sport.objects.get(name=sport)
        team_list = Teams.objects.filter(sport=sport.id)
        success = True
        message = f"Send From Django API mix "
        team_serializer = TeamsSerializer(team_list, many=True, context={'request': request})
        sport_data = {'team': team_serializer.data, }

        data = {'success': success, 'data': sport_data, 'message': message, }
        return JsonResponse(data, safe=False)
    except Exception as e:

        success = False
        message = f"error in get data   {e}  "

        sport_data = {'team': [],

                      }

        data = {'success': success, 'data': sport_data, 'message': message,

                }
        return JsonResponse(data, safe=False)


def SportTeamsApiDetails(request, team_id):
    try:
        team_list = Teams.objects.filter(id=team_id)
        success = True
        message = f"Send From Django API mix {team_id} "
        team_serializer = TeamsSerializer(team_list, many=True, context={'request': request})
        sport_data = {'team': team_serializer.data, }

        data = {'success': success, 'data': sport_data, 'message': message, }
        return JsonResponse(data, safe=False)
    except:
        success = False
        message = f"error in get data  News Details  "

        sport_data = {'team': [],

                      }

        data = {'success': success, 'data': sport_data, 'message': message,

                }
        return JsonResponse(data, safe=False)


####################### Playrs Api #################


def PlayersApiList(request):
    try:
        paginator = PageNumberPagination()
        paginator.page_size = 10
        players_list = Players.objects.all()
        success = True
        message = f"Send From Django API mix "
        players_serializer = PlayersSerializer(players_list, many=True, context={'request': request})
        sport_data = {'player': players_serializer.data, }
        data = {'success': success, 'data': sport_data, 'message': message,

                }
        return JsonResponse(data, safe=False)
    except Exception as e:
        print(e)
        success = False
        message = f"error in get data no data no data with this country"

        sport_data = {

            'player': [], }
    data = {'success': success, 'data': sport_data, 'message': message,

            }
    return JsonResponse(data, safe=False)


def PlayersApiDetails(request, playerid):
    try:
        players_list = Players.objects.filter(id=playerid)
        # mpr = MatchPlayerReport.objects.filter(player=playerid)
        # psr = PlayerStatics.objects.filter(player=playerid)
        success = True
        message = f"Send From Django API mix {playerid} "
        players_serializer = PlayersSerializer(players_list, many=True, context={'request': request})
        # mpr_serializer = MatchPlayerReportSerializer(mpr, many=True)
        # psr_serializer = PlayerStaticsSerializer(psr, many=True)
        sport_data = {'players': players_serializer.data,  # 'match_report': mpr_serializer.data,
                      # 'player_statics': psr_serializer.data,

                      }

        data = {'success': success, 'data': sport_data, 'message': message,

                }
        return JsonResponse(data, safe=True)
    except Exception as e:
        print(e)
        success = False
        message = f"error in get data {e}  "

        sport_data = {'players': [],  # 'match_report': [],
                      # 'player_statics': [],

                      }

        data = {'success': success, 'data': sport_data, 'message': message,

                }
        return JsonResponse(data, safe=True)


def PlayersBySportApiList(request, sport_name, team_id):
    try:
        sport = Sport.objects.get(name=sport_name)
    except Exception as e:
        sport = Sport.objects.create(name=sport_name)
    try:
        team = Teams.objects.get(id=team_id)

        players_list = Players.objects.filter(sport=sport.id, team=team.id).order_by('name')

        success = True
        message = f"Send From Django API mix "
        players_serializer = PlayersSerializer(players_list, many=True, context={'request': request})
        sport_data = {'sport': sport_name, 'players': players_serializer.data, }

        data = {'success': success, 'data': sport_data, 'message': message, }

        return JsonResponse(data, safe=False)
    except Exception as e:
        success = False
        message = f"error in get data   {e}  "
        sport_data = {'sport': sport_name, 'table': [], }
        data = {'success': success, 'data': sport_data, 'message': message, }
        return JsonResponse(data, safe=False)


################## News ##################

def SportNewsByCountryApiList(request, ):
    try:
        news_list = BlogArticle.objects.all().order_by('-created_at')[0:20]
        success = True
        message = f"Send From Django API mix "
        news_serializer = AdminBlogArticleSerializer(news_list, many=True, context={'request': request})
        sport_data = { 'articles': news_serializer.data, }
    except Exception as e:
        success = False
        message = f"error in get data no data no data with this country"

        sport_data = {'articles': [], }

    data = {'success': success, 'data': sport_data, 'message': message, }
    return JsonResponse(data, safe=False)


def SportNewsApiDetails(request, article_id):
    try:
        news_list = BlogArticle.objects.filter(id=article_id)
        success = True
        message = f"Send From Django API News Details {article_id} "
        news_serializer = AdminBlogArticleDetailsSerializer(news_list, many=True, context={'request': request})
        sport_data = {'articles': news_serializer.data,

                      }

        data = {'success': success, 'data': sport_data, 'message': message,

                }
        return JsonResponse(data, safe=True)
    except Exception as e:
        print(e)
        success = False
        message = f"error in get data  News Details  "

        sport_data = {'articles': [],

                      }

        data = {'success': success, 'data': sport_data, 'message': message,

                }
        return JsonResponse(data, safe=True)


def SportVideosApiList(request, ):
    try:
        video_list = BlogVideo.objects.all()
        success = True
        message = f"Send From Django API  "
        video_serializer = AdminBlogVideoSerializer(video_list, many=True, context={'request': request})
        serializer = {'video': video_serializer.data, }
        data = {'success': success, 'data': serializer, 'message': message, }
        return JsonResponse(data, safe=False)
    except Exception as e:
        print('error', e)
        success = False
        message = f"error in get data    "
        data = {'success': success, 'data': [], 'message': message, }
        return JsonResponse(data, safe=False)


def SportVideosByCountryApiList(request, country, sport):
    print()
    if country == '' or country == None or country == 'all' or country == ':country':
        country = 'Kuwait'
    else:
        country = country
    if sport == '' or sport == None or sport == 'all' or sport == ':sport':
        sport = 'Volleyball'
    sport_list = Sport.objects.filter(name=sport, )
    if sport_list.count() > 0:
        get_sport = Sport.objects.get(name=sport)
        video_list = BlogVideo.objects.filter(sport=get_sport.id, country=country)
        success = True
        message = f"Send From Django API mix {country}"

        video_serializer = AdminBlogVideoSerializer(video_list, many=True, context={'request': request})
        sport_data = {'country': country,  'video': video_serializer.data, }

    else:
        success = False
        message = f"error in get data no data no data with this country {country} or sport {sport}"

        sport_data = {'country': country, 'sport': [], 'video': [],

                      }

    data = {'success': success, 'data': sport_data, 'message': message,

            }
    return JsonResponse(data, safe=False)



def SportTablesApiList(request, group):
    try:
        table_list =LeagueSeasonTable.objects.get(id=group)
        teams_table = TeamSeasonTable.objects.filter(table = table_list.id)

        success = True
        message = f"Send From Django API mix table "
        table_serializer = LeagueSeasonTableSerializer(table_list, many=False, context={'request': request})
        team_serializer = TeamSeasonTableSerializer(teams_table, many=True, context={'request': request})
        sport_data = {'sport': 'volleyball', 'table': table_serializer.data,
                        'teams': team_serializer.data, }

        data = {'success': success, 'data': sport_data, 'message': message, }

        return JsonResponse(data, safe=False)
    except Exception as e:
        success = False
        message = f"error in get data table  {e}  "
        sport_data = {'sport': 'volleyball', 'table': [], }
        data = {'success': success, 'data': sport_data, 'message': message, }
        return JsonResponse(data, safe=False)


def SportTeamsPlayersApiDetails(request,team_id,league_id):
    try:
        team = Teams.objects.get(id=team_id)
        league = Leagues.objects.get(id=league_id)



        players_list = Players.objects.filter(team=team.id, league=league.id).order_by('name')
        success = True
        message = f"Send From Django API mix {team_id}// {league_id} "
        players_serializer = PlayersSerializer(players_list, many=True, context={'request': request})
        sport_data = {'team': team.name, 'players': players_serializer.data, }

        data = {'success': success,'message': message, 'data': sport_data,  }

        return JsonResponse(data, safe=False,status=200)
    except Exception as e:
        success = False
        message = f"error in get data   {e}  "
        sport_data = {'team':team_id, 'players': [], }
        data = {'success': success, 'data': sport_data, 'message': message, }
        return JsonResponse(data, safe=False,status=200)



def SportPlayersApiDetails(request,player_id):
    try:
        players_list = Players.objects.filter(id=player_id)
        success = True
        message = f"Send From Django API mix {player_id} "
        players_serializer = PlayersSerializer(players_list, many=True, context={'request': request})
        sport_data = {'players': players_serializer.data, }

        data = {'success': success, 'data': sport_data, 'message': message, }

        return JsonResponse(data, safe=False,status=200)
    except Exception as e:
        success = False
        message = f"error in get data   {e}  "
        sport_data = {'players': [], }
        data = {'success': success, 'data': sport_data, 'message': message, }
        return JsonResponse(data, safe=False,status=200)
from datetime import datetime, timedelta

import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from api.v3.serializers.sport.monk import *
from api.v3.serializers.sport.sport import *
from apps.sport.models.models import *
from apps.sport.models.monks import *
from apps.sport.views.monks import AdminMonksFixturesGetData
from core.models.blog import BlogArticle, BlogVideo
from core.utils.pagination import PageNumberPagination
# from core.views.notifications import AdminFcmNotifications
from digit_sport import settings

api_key = settings.SPORT_MONKS_TOKEN
base_url = settings.SPORT_MONKS_URL


#################### Volleyball ##################
def LeaguesBySportApiList(request, sport_name):
    try:
        sport = Sport.objects.get(name=sport_name)
    except Exception as e:
        sport = Sport.objects.create(name=sport_name)
    try:
        league_list = Leagues.objects.filter(sport=sport.id)
        success = True
        message = f"Send From Django API mix "
        league_serializer = LeaguesByItemSerializer(league_list, many=True ,context={'request': request})
        sport_data = {'leagues': league_serializer.data, }

        data = {'success': success, 'data': sport_data, 'message': message, }

        return JsonResponse(data, safe=False,status=200)
    except Exception as e:
        success = False
        message = f"error in get data   {e}  "
        sport_data = {'leagues': [], }
        data = {'success': success, 'data': sport_data, 'message': message, }
        return JsonResponse(data, safe=False,status=404)



def MatchesBySportApiList(request,sport_name,leagueId):
    try:
        sport = Sport.objects.get(name=sport_name)
    except Exception as e:
        sport = Sport.objects.create(name=sport_name)
    if leagueId !='null' :
        league = Leagues.objects.get(id=leagueId)
    else:
        league = Leagues.objects.filter(sport=sport.id).first()
        match_league = Leagues.objects.filter(sport=sport.id)

    matches_list = Match.objects.filter(sport=sport.id,league=league).order_by('-start_time')

    try:
        success = True
        message = f"Send From Django API mix "
        league_serializer = LeaguesByItemSerializer(league, many=False,context={'request': request})
        match_serializer = MatchSerializer(matches_list, many=True,context={'request': request})

        sport_data = {
            'leagues': league_serializer.data,
            'matches': match_serializer.data,
                      }

        data = {'success': success, 'data': sport_data, 'message': message,
                }
        return JsonResponse(data, safe=False)
    except Exception as e:
        success = False
        message = f"error in get data match {e} "

        sport_data = {
            'leagues': [],
            'matches': [],

                      }

        data = {'success': success, 'data': sport_data, 'message': message,

                }
        return JsonResponse(data, safe=False)


def MatchesBySportAndDateApiList(request,sport_name,type,leagueId ):
    round_list = []
    matches_list = []
    first_date = datetime.now()
    last_date = datetime.now()
    order_by = 'start_time'
    try:
        sport = Sport.objects.get(name=sport_name)
    except Exception as e:
        sport = Sport.objects.create(name=sport_name)
    if leagueId != 'null':
        league = Leagues.objects.get(id=leagueId)
        match_league = Leagues.objects.filter(id=leagueId)
    else:

        match_league = Leagues.objects.filter(sport=sport.id)
    if type == 'current':
        first_date = datetime.now() - timedelta(hours=1)
        last_date = datetime.now() + timedelta(days=90)
        order_by = 'start_time'
    elif type == 'last':
        first_date = datetime.now() - timedelta(days=90)
        last_date = datetime.now() - timedelta(hours=1)
        order_by = 'start_time'
    if sport_name == 'volleyball':
        round_list = []
        matches_list = Match.objects.filter(sport=sport.id, start_time__range=[first_date, last_date]).order_by(
            order_by)
    elif sport_name == 'handball':
        round_list = Round.objects.filter(sport=sport.id)
        matches_list = []
    try:
        success = True
        message = f"Send From Django volleyball {type} "
        match_serializer = MatchSerializer(matches_list, many=True,context={'request': request})
        league_serializer = LeaguesByItemSerializer(match_league, many=True,context={'request': request})
        round_serializer = RoundSerializer(round_list, many=True, context={'first_date': first_date, 'last_date': last_date,'leagueId':leagueId,
                                                                           'request': request})
        sport_data = {
            'rounds': round_serializer.data,
            'leagues': league_serializer.data,
            'matches': match_serializer.data,
            }
        data = {'success': success, 'data': sport_data, 'message': message,
                }
        return JsonResponse(data, safe=False)
    except Exception as e:
        success = False
        message = f"error in get data   {e} {type} "
        sport_data = {
            'leagues': [],
            'matches': [],
            'rounds': [],


                      }

        data = {'success': success, 'data': sport_data, 'message': message,

                }
        return JsonResponse(data, safe=False)

def MatchDetailsApi(request, match_id):
    try:
        matches_list = Match.objects.filter(id=match_id)
        get_match = Match.objects.get(id=match_id)
        get_league = Leagues.objects.filter(id=get_match.league.id)
        home_team = Teams.objects.filter(id=get_match.home_team.id)
        away_team = Teams.objects.filter(id=get_match.away_team.id)
        home_team_players = MatchTeamPlayer.objects.filter(match=match_id, team=get_match.home_team.id)
        away_team_players = MatchTeamPlayer.objects.filter(match=match_id, team=get_match.away_team.id)
        summary_list = MatchSummary.objects.filter(match=match_id)
        statics_list = MatchStatics.objects.filter(match=match_id)
        goals_list = MatchGoals.objects.filter(match=match_id)
        table_list = SeasonTable.objects.filter(league=get_match.league.id)


        league_serializer = LeaguesSerializer(get_league, many=True, context={'request': request})
        match_serializer = MatchDetailsSerializer(matches_list, many=True, context={'request': request})
        home_team_serializer = TeamsSerializer(home_team, many=True, context={'request': request})
        away_team_serializer = TeamsSerializer(away_team, many=True, context={'request': request})
        home_team_players_serializer = MatchTeamPlayerSerializer(home_team_players, many=True,context={'request': request})
        away_team_players_serializer = MatchTeamPlayerSerializer(away_team_players, many=True,context={'request': request})
        summary_serializer = MatchSummarySerializer(summary_list, many=True, context={'request': request})
        statics_serializer = MatchStaticsSerializer(statics_list, many=True, context={'request': request})
        goals_serializer = MatchGoalsSerializer(goals_list, many=True, context={'request': request})
        table_serializer = SeasonTableSerializer(table_list, many=True, context={'request': request})

        sport_data = {'league': league_serializer.data,
            'matches': match_serializer.data, 'home_team': home_team_serializer.data,
                      'away_team': away_team_serializer.data, 'home_team_players': home_team_players_serializer.data,
                      'away_team_players': away_team_players_serializer.data, 'summary': summary_serializer.data,
                      'statics': statics_serializer.data, 'goals': goals_serializer.data,
                      'season_table': table_serializer.data,

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
def SeasonTableBySportApiList(request,sport_name):
    try:
        sport = Sport.objects.get(name=sport_name)
    except Exception as e:
        sport = Sport.objects.create(name=sport_name)
    try:
        sport = Sport.objects.get(name=sport_name)
        table_list = SeasonTable.objects.filter(sport=sport).order_by('position')
        success = True
        message = f"Send From Django API mix table "
        table_serializer = SeasonTableSerializer(table_list, many=True,context={'request': request})
        sport_data = {'sport': 'volleyball', 'table': table_serializer.data, }

        data = {'success': success, 'data': sport_data, 'message': message, }

        return JsonResponse(data, safe=False)
    except Exception as e:
        success = False
        message = f"error in get data table  {e}  "
        sport_data = {'sport': 'volleyball', 'table': [], }
        data = {'success': success, 'data': sport_data, 'message': message, }
        return JsonResponse(data, safe=False)

###################### TEams Api ######################
def SportTeamsApiList(request,sport):

    try:
        sport = Sport.objects.get(name=sport)
        team_list = Teams.objects.filter(sport=sport.id)
        success = True
        message = f"Send From Django API mix "
        team_serializer = TeamsSerializer(team_list, many=True,context={'request': request})
        sport_data = {'team': team_serializer.data,
                      }

        data = {'success': success, 'data': sport_data, 'message': message,
                }
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
        team_serializer = TeamsSerializer(team_list, many=True,context={'request': request})
        sport_data = {'team': team_serializer.data,
                      }

        data = {'success': success, 'data': sport_data, 'message': message,
                }
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
        players_serializer = PlayersSerializer(players_list, many=True,context={'request': request})
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
        players_serializer = PlayersSerializer(players_list, many=True,context={'request': request})
        # mpr_serializer = MatchPlayerReportSerializer(mpr, many=True)
        # psr_serializer = PlayerStaticsSerializer(psr, many=True)
        sport_data = {'players': players_serializer.data,
                        # 'match_report': mpr_serializer.data,
                        # 'player_statics': psr_serializer.data,

                      }

        data = {'success': success, 'data': sport_data, 'message': message,

                }
        return JsonResponse(data, safe=True)
    except Exception as e:
        print(e)
        success = False
        message = f"error in get data {e}  "

        sport_data = {'players': [],
                        # 'match_report': [],
                        # 'player_statics': [],

                      }

        data = {'success': success, 'data': sport_data, 'message': message,

                }
        return JsonResponse(data, safe=True)


def PlayersBySportApiList(request,sport_name,team_id):
    try:
        sport = Sport.objects.get(name=sport_name)
    except Exception as e:
        sport = Sport.objects.create(name=sport_name)
    try:
        team = Teams.objects.get(id=team_id)

        players_list = Players.objects.filter(sport=sport.id,team=team.id).order_by('name')

        success = True
        message = f"Send From Django API mix "
        players_serializer = PlayersSerializer(players_list, many=True,context={'request': request})
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

def SportNewsByCountryApiList(request,):

    sport_list = Sport.objects.all()
    if sport_list.count() > 0:

        news_list = BlogArticle.objects.all().order_by('-created_at')
        success = True
        message = f"Send From Django API mix "
        sport_serializer = SportSerializer(sport_list, many=True,context={'request': request})
        news_serializer = AdminBlogArticleSerializer(news_list, many=True,context={'request': request})
        sport_data = { 'sport': sport_serializer.data, 'articles': news_serializer.data, }

    else:
        success = False
        message = f"error in get data no data no data with this country "

        sport_data = { 'articles': [], }

    data = {'success': success, 'data': sport_data, 'message': message,

            }
    return JsonResponse(data, safe=False)


def SportNewsApiDetails(request, article_id):
    try:
        news_list = BlogArticle.objects.filter(id=article_id)
        success = True
        message = f"Send From Django API News Details {article_id} "
        news_serializer = AdminBlogArticleDetailsSerializer(news_list, many=True,context={'request': request})
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
        video_serializer = AdminBlogVideoSerializer(video_list, many=True,context={'request': request})
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
        sport_serializer = SportSerializer(sport_list, many=True,context={'request': request})
        video_serializer = AdminBlogVideoSerializer(video_list, many=True,context={'request': request})
        sport_data = {'country': country, 'sport': sport_serializer.data, 'video': video_serializer.data, }

    else:
        success = False
        message = f"error in get data no data no data with this country {country} or sport {sport}"

        sport_data = {'country': country, 'sport': [], 'video': [],

                      }

    data = {'success': success, 'data': sport_data, 'message': message,

            }
    return JsonResponse(data, safe=False)

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


#################### Volleyball ##################
def LeaguesBySportAndDateApiList(request,date, sport_name):
    try:
        sport = Sport.objects.get(name=sport_name)
    except Exception as e:
        sport = Sport.objects.create(name=sport_name)
    league_list = []
    matches = Match.objects.filter(start_time__date=date, sport=sport.id)
    print('match count', matches.count(),date)

    for item in matches:
        league_list.append(item.league.slug)
    print('league_list',league_list, matches.count())

    try:
        league_list = Leagues.objects.filter(sport=sport.id,slug__in=league_list)
        day_message = None
        if league_list.count() == 0:
            print('league_list no',league_list)

            print('league_list no 2', league_list)
            new_date = datetime.now() + timedelta(days=90)
            matches = Match.objects.filter(start_time__date__range=[date, new_date], sport=sport.id)
            match = Match.objects.filter(start_time__range=[date, new_date],
                                         sport=sport.id).first()

            print('matches found newer', matches.count(), match)
            league_list = Leagues.objects.filter(sport=sport.id,id=match.league.id)

            if match:
                new_date = match.start_time
                new_date = new_date.date()
                print('matches found newer', matches.count(), date, new_date, '::::', match.start_time)
                day_message = 'coming matches ' + str(new_date.date().day)

            else:
                print('matches not found newer', matches.count(), date, new_date)
                # new_date = datetime.now() - timedelta(days=90)
                # match = Match.objects.filter(start_time__date__range=[date, new_date], sport=sport.id).first()
                # new_date = match.start_time
                # new_date = new_date.date()
                # day_message = 'No Match For Select Day Older Match in ' + str(new_date)
                print('matches',matches.count(),date,new_date,)
        else:
            new_date = date
            day_message = None

        success = True
        message = f"Send From Django LeaguesBySportApiList {date} {new_date} "
        league_serializer = LeaguesByItemSerializer(league_list, many=True ,context={'request': request,'date':new_date})
        sport_data = {'leagues': league_serializer.data,'day':new_date, 'day_message':day_message }
        data = {'success': success, 'message': message,'data': sport_data,  }
        return JsonResponse(data, safe=False,status=HTTP_200_OK)
    except Exception as e:
        print('error LeaguesBySportApiList',e)
        success = False
        message = f"error in get data   {e}  "
        sport_data = {'leagues': [], 'day': date, 'day_message': None, }
        data = {'success': success, 'message': message, 'data': sport_data, }
        return JsonResponse(data, safe=False,status=HTTP_204_NO_CONTENT)



# def MatchesBySportApiList(request,sport_name,leagueId):
#     try:
#         sport = Sport.objects.get(name=sport_name)
#     except Exception as e:
#         sport = Sport.objects.create(name=sport_name)
#     if leagueId !='null' :
#         league = Leagues.objects.get(id=leagueId)
#     else:
#         league = Leagues.objects.filter(sport=sport.id).first()
#         match_league = Leagues.objects.filter(sport=sport.id)
#
#     matches_list = Match.objects.filter(sport=sport.id,league=league).order_by('-start_time')
#
#     try:
#         success = True
#         message = f"Send From MatchesBySportApiList "
#         league_serializer = LeaguesByItemSerializer(league, many=False,context={'request': request})
#         match_serializer = MatchSerializer(matches_list, many=True,context={'request': request})
#
#         sport_data = {
#             'leagues': league_serializer.data,
#             'matches': match_serializer.data,
#                       }
#
#         data = {'success': success, 'data': sport_data, 'message': message,
#                 }
#         return JsonResponse(data, safe=False)
#     except Exception as e:
#         success = False
#         message = f"error in get data match {e} "
#
#         sport_data = {
#             'leagues': [],
#             'matches': [],
#
#                       }
#
#         data = {'success': success, 'data': sport_data, 'message': message,
#
#                 }
#         return JsonResponse(data, safe=False)


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
        first_date = datetime.now() - timedelta(hours=3)
        last_date = datetime.now() + timedelta(days=90)
        order_by = 'start_time'
    elif type == 'last':
        first_date = datetime.now() - timedelta(days=90)
        last_date = datetime.now() - timedelta(hours=3)
        order_by = 'start_time'
    if sport_name == 'volleyball':
        round_list = Round.objects.filter(sport=sport.id)
        matches_list = Match.objects.filter(sport=sport.id, start_time__range=[first_date, last_date]).order_by(
            order_by)
    elif sport_name == 'handball':
        round_list = Round.objects.filter(sport=sport.id)
        matches_list = []
    try:
        success = True
        message = f"Send From Django {sport_name} {leagueId} {type} "
        match_serializer = MatchSerializer(matches_list, many=True,context={'request': request})
        league_serializer = LeaguesByItemSerializer(match_league, many=True,context={'request': request,'date':first_date})
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


def MatchesByDateApiList(request,date,leagueid):
    print('date',date)
    round_list = []
    matches_list = []
    first_date = datetime.now()
    last_date = datetime.now()
    order_by = 'start_time'
    leagues = Leagues.objects.filter(id=leagueid)
    league = Leagues.objects.get(id=leagueid)
    match_league = Match.objects.filter(league=leagueid,start_time__date=date)

    try:
        success = True
        message = f"Send From MatchesByDateApiList {date} "
        match_serializer = MatchSerializer(match_league, many=True,context={'request': request})
        league_serializer = LeaguesByItemSerializer(leagues, many=True,context={'request': request,'date':date})
        sport_data = {
            'leagues': league_serializer.data,
            'matches': match_serializer.data,
            'rounds': round_list,
            }
        data = {'success': success, 'data': sport_data, 'message': message,
                }
        return JsonResponse(data, safe=False)
    except Exception as e:
        success = False
        message = f"error in get data   {e} {date} "
        sport_data = {
            'leagues': [],
            'matches': [],
            'rounds': [],


                      }

        data = {'success': success, 'data': sport_data, 'message': message,

                }
        return JsonResponse(data, safe=False,status=HTTP_404_NOT_FOUND)

def MatchesBySportApiList(request,sport_name):
    round_list = []
    matches_list = []
    first_date = datetime.now()
    last_date = datetime.now() + timedelta(days=90)
    order_by = 'start_time'
    sport = Sport.objects.get(name=sport_name)
    print('sport',sport)
    leagues = Leagues.objects.filter(sport=sport)
    print('leagues',leagues)


    match_league = Match.objects.filter(sport=sport,start_time__lte=first_date, start_time__gte=last_date)
    print('match_league',match_league)

    try:
        success = True
        message = f"Send From MatchesBySportApiList {leagues} {match_league}  {first_date} {last_date} "
        match_serializer = MatchSerializer(match_league, many=True,context={'request': request})
        league_serializer = LeaguesByItemSerializer(leagues, many=True,context={'request': request,'date':first_date})
        sport_data = {
            'leagues': league_serializer.data,
            'matches': match_serializer.data,
            'rounds': round_list,
            }
        data = {'success': success,'message': message, 'data': sport_data,
                }
        return JsonResponse(data, safe=False)
    except Exception as e:
        success = False
        message = f"error in get data   {e} {first_date} "
        sport_data = {
            'leagues': [],
            'matches': [],
            'rounds': [],


                      }

        data = {'success': success, 'data': sport_data, 'message': message,

                }
        return JsonResponse(data, safe=False,status=HTTP_404_NOT_FOUND)
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
        table_list = SeasonTable.objects.filter(league=get_match.league.id, sport=get_match.sport.id,team__in=[get_match.home_team.id,get_match.away_team.id]).order_by('position')


        # league_serializer = LeaguesSerializer(get_league, many=True, context={'request': request})
        match_serializer = MatchDetailsSerializer(matches_list, many=True, context={'request': request})
        home_team_serializer = TeamsSerializer(home_team, many=True, context={'request': request})
        away_team_serializer = TeamsSerializer(away_team, many=True, context={'request': request})
        # home_team_players_serializer = MatchTeamPlayerSerializer(home_team_players, many=True,context={'request': request})
        # away_team_players_serializer = MatchTeamPlayerSerializer(away_team_players, many=True,context={'request': request})
        # summary_serializer = MatchSummarySerializer(summary_list, many=True, context={'request': request})
        statics_serializer = MatchStaticsSerializer(statics_list, many=True, context={'request': request})
        goals_serializer = MatchGoalsSerializer(goals_list, many=True, context={'request': request})
        table_serializer = SeasonTableSerializer(table_list, many=True, context={'request': request})

        sport_data = {
            # 'league': league_serializer.data,
            'matches': match_serializer.data, 'home_team': home_team_serializer.data,
                      'away_team': away_team_serializer.data,
            # 'home_team_players': home_team_players_serializer.data,
            #           'away_team_players': away_team_players_serializer.data, 'summary': summary_serializer.data,
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
def SeasonTableBySportApiList(request,sport_name,league_id):
    try:
        sport = Sport.objects.get(name=sport_name)
    except Exception as e:
        sport = Sport.objects.create(name=sport_name)
    try:
        sport = Sport.objects.get(name=sport_name)
        table_list = SeasonTable.objects.filter(sport=sport,league_id=league_id).order_by('position')
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
